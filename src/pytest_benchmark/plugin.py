from __future__ import division

import argparse
import gc
import sys
import math
from collections import defaultdict
from decimal import Decimal

import pytest
import py

from .stats import RunningStats
from .timers import compute_timer_precision
from .timers import default_timer
from .compat import XRANGE, PY3


def loadtimer(string):
    if "." not in string:
        raise argparse.ArgumentTypeError("Value for --benchmark-timer must be in dotted form. Eg: 'module.attr'.")
    mod, attr = string.rsplit(".", 1)
    if mod == 'pep418':
        if PY3:
            import time
            return getattr(time, attr)
        else:
            from . import pep418
            return getattr(pep418, attr)
    else:
        __import__(mod)
        mod = sys.modules[mod]
        return getattr(mod, attr)


def loadsort(string):
    if string not in ("min", "max", "mean", "stddev"):
        raise argparse.ArgumentTypeError("Value for --benchmark-sort must be one of: 'min', 'max', 'mean' or 'stddev'.")
    return string


def loadrounds(string):
    try:
        value = int(string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(exc)
    else:
        if value < 1:
            raise argparse.ArgumentTypeError("Value for --benchmark-rounds must be at least 1.")
        return value


def pytest_addoption(parser):
    group = parser.getgroup("benchmark")
    group.addoption(
        "--benchmark-min-time",
        action="store", type=Decimal, default=Decimal("0.0001"),
        help="Minimum time per round. Default: %(default)s"
    )
    group.addoption(
        "--benchmark-max-time",
        action="store", type=Decimal, default=Decimal("1.0"),
        help="Maximum time to spend in a benchmark. Default: %(default)s"
    )
    group.addoption(
        "--benchmark-min-rounds",
        action="store", type=loadrounds, default=5,
        help="Minimum rounds, even if total time would exceed `--max-time`. Default: %(default)s"
    )
    group.addoption(
        "--benchmark-sort",
        action="store", type=loadsort, default="min",
        help="Column to sort on. Can be one of: 'min', 'max', 'mean' or 'stddev'. Default: %(default)s"
    )
    group.addoption(
        "--benchmark-timer",
        action="store", type=loadtimer, default=default_timer,
        help="Timer to use when measuring time. Default: %(default)s"
    )
    group.addoption(
        "--benchmark-warmup",
        action="store_true", default=False,
        help="Runs the benchmarks two times. Discards data from the first run."
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


class BenchmarkStats(RunningStats):
    def __init__(self, name, group, scale):
        self.name = name
        self.group = group
        self.scale = scale
        super(BenchmarkStats, self).__init__()

    def __getitem__(self, key):
        return getattr(self, key)

    def update(self, duration):
        super(BenchmarkStats, self).update(duration / self.scale)


class BenchmarkFixture(object):
    _precisions = {}

    @classmethod
    def _get_precision(cls, timer):
        if timer in cls._precisions:
            return cls._precisions[timer]
        else:
            return cls._precisions.setdefault(timer, compute_timer_precision(timer))

    def __init__(self, name, disable_gc, timer, min_rounds, min_time, max_time, warmup, add_stats, logger, group=None):
        self._disable_gc = disable_gc
        self._name = name
        self._group = group
        self._timer = timer
        self._min_rounds = min_rounds
        self._max_time = float(max_time)
        self._min_time = float(min_time)
        self._add_stats = add_stats
        self._warmup = warmup
        self._logger = logger

    def __call__(self, function_to_benchmark):
        def runner(loops, timer=self._timer):
            loops_range = XRANGE(loops)
            gcenabled = gc.isenabled()
            if self._disable_gc:
                gc.disable()
            start = timer()
            for index in loops_range:
                function_to_benchmark()
            end = timer()
            if gcenabled:
                gc.enable()
            return end - start

        duration, scale = self._calibrate_timer(runner)

        # Choose how many time we must repeat the test
        rounds = int(math.ceil(self._max_time / duration))
        rounds = max(rounds, self._min_rounds)

        stats = BenchmarkStats(self._name, group=self._group, scale=scale)
        self._add_stats(stats)

        if self._warmup:
            for _ in XRANGE(rounds):
                runner(scale)

        for _ in XRANGE(rounds):
            stats.update(runner(scale))

        return function_to_benchmark()

    def _calibrate_timer(self, runner):
        timer_precision = self._get_precision(self._timer)
        min_time = max(self._min_time, timer_precision * 100)
        min_time_estimate = min_time / 10
        self._logger.write("")
        self._logger.write("  Timer precision: %ss" % time_format(timer_precision))
        self._logger.write("  Calibrating to target round %ss; will estimate when reaching %ss." % (
            time_format(min_time), time_format(min_time_estimate)))

        loops = 1
        while True:
            duration = runner(loops)
            self._logger.write("  Calibrate: %ss for %s iterations." % (time_format(duration), loops))

            if duration / min_time >= 0.75:
                break

            if duration >= min_time_estimate:
                # coarse estimation of the number of loops
                loops = int(min_time * loops / duration)
                self._logger.write("  Calibrate estimate: %s iterations." % loops)
            else:
                loops *= 10
        return duration, loops


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


class DiagnosticLogger(object):
    def __init__(self, verbose
                 # , capman
                 ):
        self.term = verbose and py.io.TerminalWriter()
        # self.capman = capman

    def write(self, text):
        if self.term:
            # if self.capman:
            #     self.capman.suspendcapture(in_=True)
            self.term.line(text, yellow=True)
            # if self.capman:
            #     self.capman.resumecapture()


class BenchmarkSession(object):
    def __init__(self, config):
        timer = config.getoption("benchmark_timer")
        self._options = dict(
            min_time=config.getoption("benchmark_min_time"),
            min_rounds=config.getoption("benchmark_min_rounds"),
            max_time=config.getoption("benchmark_max_time"),
            timer=timer,
            disable_gc=config.getoption("benchmark_disable_gc"),
            warmup=config.getoption("benchmark_warmup")
        )
        self._skip = config.getoption("benchmark_skip")
        self._only = config.getoption("benchmark_only")
        self._sort = config.getoption("benchmark_sort")
        self._verbose = config.getoption("benchmark_verbose")
        if self._skip and self._only:
            raise pytest.UsageError("Can't have both --benchmark-only and --benchmark-skip options.")
        self._benchmarks = []

    @pytest.fixture(scope="function")
    def benchmark(self, request):
        if self._skip:
            pytest.skip("Benchmarks are disabled.")
        else:
            node = request.node
            marker = node.get_marker("benchmark")
            options = marker.kwargs if marker else {}
            benchmark = BenchmarkFixture(
                node.name,
                add_stats=self._benchmarks.append,
                logger=DiagnosticLogger(
                    self._verbose,
                    # node.config.pluginmanager.getplugin("capturemanager")
                ),
                **dict(self._options, **options)
            )
            return benchmark

    def pytest_runtest_call(self, item, __multicall__):
        benchmark = hasattr(item, "funcargs") and item.funcargs.get("benchmark")
        if isinstance(benchmark, BenchmarkFixture):
            if self._skip:
                pytest.skip("Skipping benchmark (--benchmark-skip active).")
            else:
                __multicall__.execute()
        else:
            if self._only:
                pytest.skip("Skipping non-benchmark (--benchmark-only active).")
            else:
                __multicall__.execute()

    def pytest_terminal_summary(self, terminalreporter):
        tr = terminalreporter

        if not self._benchmarks:
            return

        timer = self._options.get('timer') or 'default'
        timer_name = timer.__module__ + "." if hasattr(timer, '__module__') else ""
        timer_name += timer.__name__ if hasattr(timer, '__name__') else repr(timer)

        groups = defaultdict(list)
        for bench in self._benchmarks:
            groups[bench.group].append(bench)
        for group, benchmarks in sorted(groups.items(), key=lambda pair: pair[0] or ""):
            worst = {}
            best = {}
            for prop in "min", "max", "mean", "stddev", "runs", "scale":
                worst[prop] = max(benchmark[prop] for benchmark in benchmarks)
            for prop in "min", "max", "mean", "stddev":
                best[prop] = min(benchmark[prop] for benchmark in benchmarks)

            unit, adjustment = time_unit(best[self._sort])
            labels = {
                "name": "Name (time in %ss)" % unit,
                "min": "Min",
                "max": "Max",
                "mean": "Mean",
                "stddev": "StdDev",
                "runs": "Rounds",
                "scale": "Iterations",
            }
            widths = {
                "name": 3 + max(len(labels["name"]), max(len(benchmark.name) for benchmark in benchmarks)),
                "runs": 2 + max(len(labels["runs"]), len(str(worst["runs"]))),
                "scale": 2 + max(len(labels["scale"]), len(str(worst["scale"]))),
            }
            for prop in "min", "max", "mean", "stddev":
                widths[prop] = 2 + max(len(labels[prop]), max(
                    len("{0:.4f}".format(benchmark[prop] * adjustment))
                    for benchmark in benchmarks
                ))
            tr.write_line(
                " benchmark{2}: {0} tests, min {1.min_rounds} rounds (of min {1.min_time:f}s),"
                " {1.max_time:f}s max time, timer: {3} ".format(
                    len(benchmarks),
                    type("", (), self._options),
                    "" if group is None else " %r" % group,
                    timer_name,
                ).center(sum(widths.values()), '-'),
                yellow=True,
            )
            tr.write_line(labels["name"].ljust(widths["name"]) + "".join(
                labels[prop].rjust(widths[prop])
                for prop in ("min", "max", "mean", "stddev", "runs", "scale")
            ))
            tr.write_line("-" * sum(widths.values()), yellow=True)

            for benchmark in benchmarks:
                tr.write(benchmark.name.ljust(widths["name"]))
                for prop in "min", "max", "mean", "stddev":
                    tr.write(
                        "{0:>{1}.4f}".format(benchmark[prop] * adjustment, widths[prop]),
                        green=benchmark[prop] == best[prop],
                        red=benchmark[prop] == worst[prop],
                        bold=True,
                    )
                for prop in "runs", "scale":
                    tr.write("{0:>{1}}".format(benchmark[prop], widths[prop]))
                tr.write("\n")

            tr.write_line("-" * sum(widths.values()), yellow=True)
            tr.write_line("")


def pytest_runtest_setup(item):
    benchmark = item.get_marker("benchmark")
    if benchmark:
        if benchmark.args:
            raise ValueError("benchmark mark can't have positional arguments.")
        for name in benchmark.kwargs:
            if name not in ("max_time", "min_rounds", "min_time", "timer", "group", "disable_gc", "warmup"):
                raise ValueError("benchmark mark can't have %r keyword argument." % name)


def pytest_configure(config):
    config.addinivalue_line("markers", "benchmark: mark a test with custom benchmark settings.")
    config.pluginmanager.register(BenchmarkSession(config), "pytest-benchmark")
