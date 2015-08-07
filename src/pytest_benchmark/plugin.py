from __future__ import division, print_function

from collections import defaultdict
from decimal import Decimal
import argparse
from datetime import datetime
import gc
import json
import platform
import math
import sys
import time

import py
import pytest
from .compat import PY3
from .compat import XRANGE
from .stats import Stats
from .timers import compute_timer_precision
from .timers import default_timer
from .utils import first_or_false
from .utils import get_commit_id
from .utils import get_current_time


class NameWrapper(object):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        name = self.target.__module__ + "." if hasattr(self.target, '__module__') else ""
        name += self.target.__name__ if hasattr(self.target, '__name__') else repr(self.target)
        return name

    def __repr__(self):
        return "NameWrapper(%s)" % repr(self.target)


def load_timer(string):
    if "." not in string:
        raise argparse.ArgumentTypeError("Value for --benchmark-timer must be in dotted form. Eg: 'module.attr'.")
    mod, attr = string.rsplit(".", 1)
    if mod == 'pep418':
        if PY3:
            import time
            return NameWrapper(getattr(time, attr))
        else:
            from . import pep418
            return NameWrapper(getattr(pep418, attr))
    else:
        __import__(mod)
        mod = sys.modules[mod]
        return NameWrapper(getattr(mod, attr))


def parse_timer(string):
    return str(load_timer(string))


def parse_sort(string):
    if string not in ("min", "max", "mean", "stddev"):
        raise argparse.ArgumentTypeError("Value for --benchmark-sort must be one of: 'min', 'max', 'mean' or 'stddev'.")
    return string


def parse_rounds(string):
    try:
        value = int(string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(exc)
    else:
        if value < 1:
            raise argparse.ArgumentTypeError("Value for --benchmark-rounds must be at least 1.")
        return value


def parse_seconds(string):
    try:
        return SecondsDecimal(string).as_string
    except Exception as exc:
        raise argparse.ArgumentTypeError("Invalid decimal value %r: %r" % (string, exc))


def pytest_addoption(parser):
    group = parser.getgroup("benchmark")
    group.addoption(
        "--benchmark-min-time",
        metavar="SECONDS", type=parse_seconds, default="0.000025",
        help="Minimum time per round in seconds. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-max-time",
        metavar="SECONDS", type=parse_seconds, default="1.0",
        help="Maximum time to spend in a benchmark in seconds. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-min-rounds",
        metavar="NUM", type=parse_rounds, default=5,
        help="Minimum rounds, even if total time would exceed `--max-time`. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-sort",
        metavar="COL", type=parse_sort, default="min",
        help="Column to sort on. Can be one of: 'min', 'max', 'mean' or 'stddev'. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-group-by",
        metavar="LABEL", default="group",
        help="How to group tests. Can be one of: 'group', 'name' or 'params'. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-timer",
        metavar="FUNC", type=parse_timer, default=str(NameWrapper(default_timer)),
        help="Timer to use when measuring time. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-warmup",
        action="store_true", default=False,
        help="Activates warmup. Will run the test function up to number of times in the calibration phase. "
             "See `--benchmark-warmup-iterations`. Note: Even the warmup phase obeys --benchmark-max-time."
    )
    group.addoption(
        "--benchmark-warmup-iterations",
        metavar="NUM", type=int, default=100000,
        help="Max number of iterations to run in the warmup phase. Default: %(default)r"
    )
    group.addoption(
        "--benchmark-verbose",
        action="store_true", default=False,
        help="Dump diagnostic and progress information."
    )
    group.addoption(
        "--benchmark-disable-gc",
        action="store_true", default=False,
        help="Disable GC during benchmarks."
    )
    group.addoption(
        "--benchmark-skip",
        action="store_true", default=False,
        help="Skip running any benchmarks."
    )
    group.addoption(
        "--benchmark-only",
        action="store_true", default=False,
        help="Only run benchmarks."
    )
    commit_id = get_commit_id()
    group.addoption(
        "--benchmark-save",
        action='append', metavar="NAME", nargs="?", default=[], const=commit_id,
        help="Save the current run into 'STORAGE-PATH/counter-NAME.json'. Default: %r" % commit_id
    )
    group.addoption(
        "--benchmark-autosave",
        action="store_true",
        help="Autosave the current run into 'STORAGE-PATH/counter-commit_id.json",
    )
    group.addoption(
        "--benchmark-compare",
        metavar="NUM", nargs="?",
        help="Compare the current run against run NUM or the latest saved run if unspecified."
    )
    group.addoption(
        "--benchmark-storage",
        metavar="STORAGE-PATH", default="./.benchmarks/",
        help="Specify a different path to store the runs (when --benchmark-save or --benchmark-autosave are used). "
             "Default: %(default)r",
    )
    prefix = "benchmark_%s" % get_current_time()
    group.addoption(
        "--benchmark-histogram",
        action='append', metavar="FILENAME-PREFIX", nargs="?", default=[], const=prefix,
        help="Plot graphs of min/max/avg/stddev over time in FILENAME-PREFIX-test_name.svg. Default: %r" % prefix
    )
    group.addoption(
        "--benchmark-json",
        metavar="PATH", type=argparse.FileType('w'),
        help="Dump a JSON report into PATH."
    )


def pytest_addhooks(pluginmanager):
    from . import hookspec

    method = getattr(pluginmanager, "add_hookspecs", None)
    if method is None:
        method = pluginmanager.addhooks
    method(hookspec)


class BenchmarkStats(object):
    def __init__(self, name, group, iterations, options):
        self.name = name
        self.group = group
        self.iterations = iterations
        self.stats = Stats()
        self.options = options

    def __getitem__(self, key):
        try:
            return getattr(self.stats, key)
        except AttributeError:
            return getattr(self, key)

    def json(self):
        out = {
            field: getattr(self.stats, field)
            for field in self.stats.fields
        }
        out['data'] = self.stats.data
        return out

    def update(self, duration):
        self.stats.update(duration / self.iterations)


class BenchmarkFixture(object):
    _precisions = {}

    @classmethod
    def _get_precision(cls, timer):
        if timer in cls._precisions:
            return cls._precisions[timer]
        else:
            return cls._precisions.setdefault(timer, compute_timer_precision(timer))

    def __init__(self, name, disable_gc, timer, min_rounds, min_time, max_time, warmup, warmup_iterations,
                 add_stats, logger, group=None):
        self._disable_gc = disable_gc
        self._name = name
        self._group = group
        self._timer = timer.target
        self._min_rounds = min_rounds
        self._max_time = float(max_time)
        self._min_time = float(min_time)
        self._add_stats = add_stats
        self._warmup = warmup and warmup_iterations
        self._logger = logger

    def __call__(self, function_to_benchmark, *args, **kwargs):
        def runner(loops_range, timer=self._timer):
            gcenabled = gc.isenabled()
            if self._disable_gc:
                gc.disable()
            start = timer()
            for _ in loops_range:
                function_to_benchmark(*args, **kwargs)
            end = timer()
            if gcenabled:
                gc.enable()
            return end - start

        duration, iterations, loops_range = self._calibrate_timer(runner)

        # Choose how many time we must repeat the test
        rounds = int(math.ceil(self._max_time / duration))
        rounds = max(rounds, self._min_rounds)

        stats = BenchmarkStats(self._name, group=self._group, iterations=iterations, options={
            "disable_gc": self._disable_gc,
            "timer": self._timer,
            "min_rounds": self._min_rounds,
            "max_time": self._max_time,
            "min_time": self._min_time,
            "warmup": self._warmup,
        })
        self._add_stats(stats)

        self._logger.write("  Running %s rounds x %s iterations ..." % (rounds, iterations), yellow=True, bold=True)
        run_start = time.time()
        if self._warmup:
            warmup_rounds = min(rounds, max(1, int(self._warmup / iterations)))
            self._logger.write("  Warmup %s rounds x %s iterations ..." % (warmup_rounds, iterations))
            for _ in XRANGE(warmup_rounds):
                runner(loops_range)
        for _ in XRANGE(rounds):
            stats.update(runner(loops_range))
        self._logger.write("  Ran for %ss." % time_format(time.time() - run_start), yellow=True, bold=True)

        return function_to_benchmark(*args, **kwargs)

    def _calibrate_timer(self, runner):
        timer_precision = self._get_precision(self._timer)
        min_time = max(self._min_time, timer_precision * 100)
        min_time_estimate = min_time / 10
        self._logger.write("")
        self._logger.write("  Timer precision: %ss" % time_format(timer_precision), yellow=True, bold=True)
        self._logger.write("  Calibrating to target round %ss; will estimate when reaching %ss." % (
            time_format(min_time), time_format(min_time_estimate)), yellow=True, bold=True)

        loops = 1
        while True:
            loops_range = XRANGE(loops)
            duration = runner(loops_range)
            if self._warmup:
                warmup_start = time.time()
                warmup_iterations = 0
                warmup_rounds = 0
                while time.time() - warmup_start < self._max_time and warmup_iterations < self._warmup:
                    duration = min(duration, runner(loops_range))
                    warmup_rounds += 1
                    warmup_iterations += loops
                self._logger.write("    Warmup: %ss (%s x %s iterations)." % (
                    time_format(time.time() - warmup_start),
                    warmup_rounds, loops
                ))

            self._logger.write("    Measured %s iterations: %ss." % (loops, time_format(duration)), yellow=True)
            if duration / min_time >= 0.75:
                break

            if duration >= min_time_estimate:
                # coarse estimation of the number of loops
                loops = int(min_time * loops / duration)
                self._logger.write("    Estimating %s iterations." % loops, green=True)
                if loops == 1:
                    # If we got a single loop then bail early - nothing to calibrate if the the
                    # test function is 100 times slower than the timer resolution.
                    loops_range = XRANGE(loops)
                    break
            else:
                loops *= 10
        return duration, loops, loops_range


def time_unit(value):
    if value < 1e-6:
        return "n", 1e9
    elif value < 1e-3:
        return "u", 1e6
    elif value < 1:
        return "m", 1e3
    else:
        return "", 1.


def time_format(value):
    unit, adjustment = time_unit(value)
    return "{0:.2f}{1:s}".format(value * adjustment, unit)


class SecondsDecimal(Decimal):
    def __float__(self):
        return float(super(SecondsDecimal, self).__str__())

    def __str__(self):
        return "{0}s".format(time_format(float(super(SecondsDecimal, self).__str__())))

    @property
    def as_string(self):
        return super(SecondsDecimal, self).__str__()


class DiagnosticLogger(object):
    def __init__(self, verbose, capman):
        if capman:
            capman.suspendcapture(in_=True)
        self.term = verbose and py.io.TerminalWriter(file=sys.stderr)
        if capman:
            capman.resumecapture()
        self.capman = capman

    def write(self, text, **kwargs):
        if self.term:
            if self.capman:
                self.capman.suspendcapture(in_=True)
            self.term.line(text, **kwargs)
            if self.capman:
                self.capman.resumecapture()


class BenchmarkSession(object):
    def __init__(self, config):
        timer = config.getoption("benchmark_timer")
        self._options = dict(
            min_time=SecondsDecimal(config.getoption("benchmark_min_time")),
            min_rounds=config.getoption("benchmark_min_rounds"),
            max_time=SecondsDecimal(config.getoption("benchmark_max_time")),
            timer=load_timer(timer),
            disable_gc=config.getoption("benchmark_disable_gc"),
            warmup=config.getoption("benchmark_warmup"),
            warmup_iterations=config.getoption("benchmark_warmup_iterations"),
        )
        self._skip = config.getoption("benchmark_skip")
        if config.getoption("dist", "no") != "no" and not self._skip:
            tr = config.pluginmanager.getplugin('terminalreporter')
            tr.write_sep("-", red=True, bold=True)
            tr.write_line(
                "WARNING: Benchmarks are automatically skipped because xdist plugin is active."
                "Benchmarks cannot be performed reliably in a parallelized environment.",
                red=True
            )
            tr.write_sep("-", red=True, bold=True)
            self._skip = True
        if hasattr(config, "slaveinput"):
            self._skip = True

        self._only = config.getoption("benchmark_only")
        self._sort = config.getoption("benchmark_sort")
        self._verbose = config.getoption("benchmark_verbose")
        if self._skip and self._only:
            raise pytest.UsageError("Can't have both --benchmark-only and --benchmark-skip options.")
        self._benchmarks = []

        print("save:", repr(config.getoption("benchmark_save")))
        print("autosave:", repr(config.getoption("benchmark_autosave")))
        print("compare:", repr(config.getoption("benchmark_compare")))
        print("storage:", repr(config.getoption("benchmark_storage")))
        print("histogram:", repr(config.getoption("benchmark_histogram")))
        print("json:", repr(config.getoption("benchmark_json")))
        print("group_by:", repr(config.getoption("benchmark_group_by")))

        self._save = first_or_false(config.getoption("benchmark_save"))
        self._autosave = config.getoption("benchmark_autosave")
        self._compare = config.getoption("benchmark_compare")
        self._storage = config.getoption("benchmark_storage")
        self._histogram = first_or_false(config.getoption("benchmark_histogram"))
        self._json = config.getoption("benchmark_json")
        self._group_by = config.getoption("benchmark_group_by")


def pytest_runtest_call(item, __multicall__):
    benchmarksession = item.config._benchmarksession

    benchmark = hasattr(item, "funcargs") and item.funcargs.get("benchmark")
    if isinstance(benchmark, BenchmarkFixture):
        if benchmarksession._skip:
            pytest.skip("Skipping benchmark (--benchmark-skip active).")
        else:
            __multicall__.execute()
    else:
        if benchmarksession._only:
            pytest.skip("Skipping non-benchmark (--benchmark-only active).")
        else:
            __multicall__.execute()


def pytest_benchmark_group_stats(benchmarks, group_by):
    groups = defaultdict(list)
    for bench in benchmarks:
        groups[bench.group].append(bench)
    return sorted(groups.items(), key=lambda pair: pair[0] or "")


def pytest_terminal_summary(terminalreporter):
    tr = terminalreporter
    config = tr.config
    bs = config._benchmarksession

    if not bs._benchmarks:
        return

    if bs._json or bs._save or bs._autosave:
        output_json = config.hook.pytest_benchmark_generate_json(config=config, benchmarks=bs._benchmarks)
        config.hook.pytest_benchmark_update_json(config=config, benchmarks=bs._benchmarks, output_json=output_json)

        if bs._json:
            with bs._json as fh:
                fh.write(json.dumps(output_json, indent=4))

    timer = bs._options.get('timer')
    for group, benchmarks in config.hook.pytest_benchmark_group_stats(
            config=config,
            benchmarks=bs._benchmarks,
            group_by=bs._group_by
    ):
        worst = {}
        best = {}
        if len(benchmarks) > 1:
            for prop in "min", "max", "mean", "stddev":
                worst[prop] = max(bench[prop] for bench in benchmarks)
                best[prop] = min(bench[prop] for bench in benchmarks)
        for prop in "rounds", "iterations":
            worst[prop] = max(benchmark[prop] for benchmark in benchmarks)

        unit, adjustment = time_unit(best.get(bs._sort, benchmarks[0][bs._sort]))
        labels = {
            "name": "Name (time in %ss)" % unit,
            "min": "Min",
            "max": "Max",
            "mean": "Mean",
            "stddev": "StdDev",
            "rounds": "Rounds",
            "iterations": "Iterations",
        }
        widths = {
            "name": 3 + max(len(labels["name"]), max(len(benchmark.name) for benchmark in benchmarks)),
            "rounds": 2 + max(len(labels["rounds"]), len(str(worst["rounds"]))),
            "iterations": 2 + max(len(labels["iterations"]), len(str(worst["iterations"]))),
        }
        for prop in "min", "max", "mean", "stddev":
            widths[prop] = 2 + max(len(labels[prop]), max(
                len("{0:.4f}".format(benchmark[prop] * adjustment))
                for benchmark in benchmarks
            ))

        tr.write_line(
            (" benchmark%(name)s: %(count)s tests, min %(min_rounds)s rounds (of min %(min_time)s),"
             " %(max_time)s max time, timer: %(timer)s " % dict(
                bs._options,
                count=len(benchmarks),
                name="" if group is None else " %r" % group,
                timer=timer,
            )).center(sum(widths.values()), '-'),
            yellow=True,
        )
        tr.write_line(labels["name"].ljust(widths["name"]) + "".join(
            labels[prop].rjust(widths[prop])
            for prop in ("min", "max", "mean", "stddev", "rounds", "iterations")
        ))
        tr.write_line("-" * sum(widths.values()), yellow=True)

        for benchmark in benchmarks:
            tr.write(benchmark.name.ljust(widths["name"]))
            for prop in "min", "max", "mean", "stddev":
                tr.write(
                    "{0:>{1}.4f}".format(benchmark[prop] * adjustment, widths[prop]),
                    green=benchmark[prop] == best.get(prop),
                    red=benchmark[prop] == worst.get(prop),
                    bold=True,
                )
            for prop in "rounds", "iterations":
                tr.write("{0:>{1}}".format(benchmark[prop], widths[prop]))
            tr.write("\n")

        tr.write_line("-" * sum(widths.values()), yellow=True)
        tr.write_line("")


def pytest_benchmark_generate_machine_info():
    return {
        "node": platform.node(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "python_compiler": platform.python_compiler(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "release": platform.release(),
        "system": platform.system()
    }


def pytest_benchmark_generate_commit_info():
    return {
        "id": get_commit_id(),
    }


def pytest_benchmark_generate_json(config, benchmarks):
    machine_info = config.hook.pytest_benchmark_generate_machine_info(config=config)
    config.hook.pytest_benchmark_update_machine_info(config=config, machine_info=machine_info)

    commit_info = config.hook.pytest_benchmark_generate_commit_info(config=config)
    config.hook.pytest_benchmark_update_commit_info(config=config, commit_info=commit_info)

    benchmarks_json = []
    output_json = {
        'machine_info': machine_info,
        'commit_info': commit_info,
        'benchmarks': benchmarks_json,
        'datetime': datetime.utcnow().isoformat(),
    }
    for bench in benchmarks:
        benchmarks_json.append({
            'group': bench.group,
            'name': bench.name,
            'stats': bench.json(),
            'options': dict(
                iterations=bench.iterations,
                **{k: v.__name__ if callable(v) else v for k, v in bench.options.items()}
            )
        })
    return output_json


@pytest.fixture(scope="function")
def benchmark(request):
    benchmarksession = request.config._benchmarksession

    if benchmarksession._skip:
        pytest.skip("Benchmarks are disabled.")
    else:
        node = request.node
        marker = node.get_marker("benchmark")
        options = marker.kwargs if marker else {}
        if 'timer' in options:
            options['timer'] = NameWrapper(options['timer'])
        benchmark = BenchmarkFixture(
            node.name,
            add_stats=benchmarksession._benchmarks.append,
            logger=DiagnosticLogger(
                benchmarksession._verbose,
                request.config.pluginmanager.getplugin("capturemanager")
            ),
            **dict(benchmarksession._options, **options)
        )

        return benchmark


@pytest.fixture(scope="function")
def benchmark_weave(benchmark):
    try:
        import aspectlib
    except ImportError as exc:
        raise ImportError(exc.args, "Please install aspectlib or pytest-benchmark[aspect]")

    def aspect(function):
        def wrapper(*args, **kwargs):
            return benchmark(function, *args, **kwargs)

        return wrapper

    def weave(target, **kwargs):
        return aspectlib.weave(target, aspect, **kwargs)

    return weave


def pytest_runtest_setup(item):
    benchmark = item.get_marker("benchmark")
    if benchmark:
        if benchmark.args:
            raise ValueError("benchmark mark can't have positional arguments.")
        for name in benchmark.kwargs:
            if name not in (
            "max_time", "min_rounds", "min_time", "timer", "group", "disable_gc", "warmup", "warmup_iterations"):
                raise ValueError("benchmark mark can't have %r keyword argument." % name)


def pytest_configure(config, __multicall__):
    __multicall__.execute()  # force the other plugins to initialise
    config.addinivalue_line("markers", "benchmark: mark a test with custom benchmark settings.")
    config._benchmarksession = BenchmarkSession(config)
    config.pluginmanager.register(config._benchmarksession, "pytest-benchmark")
