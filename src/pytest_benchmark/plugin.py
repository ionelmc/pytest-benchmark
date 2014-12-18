from __future__ import division

import argparse
import gc
import sys
import time
try:
    from __pypy__.time import clock_gettime
    from __pypy__.time import CLOCK_MONOTONIC
    default_timer = lambda: clock_gettime(CLOCK_MONOTONIC)
except ImportError:
    from timeit import default_timer
from collections import defaultdict, namedtuple
from decimal import Decimal

import pytest

from .stats import RunningStats

PY3 = sys.version_info[0] == 3


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


def loadscale(string):
    if string not in ("min", "max", "mean", "stddev"):
        raise argparse.ArgumentTypeError("Value for --benchmark-scale must be one of: 'min', 'max', 'mean' or 'stddev'.")
    return string


def pytest_addoption(parser):
    group = parser.getgroup("benchmark")
    group.addoption(
        "--benchmark-max-time",
        action="store", type=Decimal, default=Decimal("0.5"),
        help="Maximum time to spend in a benchmark (including overhead)."
    )
    group.addoption(
        "--benchmark-max-iterations",
        action="store", type=int, default=Default(5000),
        help="Maximum iterations to do."
    )
    group.addoption(
        "--benchmark-min-iterations",
        action="store", type=int, default=Default(5),
        help="Minium iterations, even if total time would exceed `max-time`."
    )
    group.addoption(
        "--benchmark-scale",
        action="store", type=loadscale, default="min",
        help="Minium iterations, even if total time would exceed `max-time`."
    )
    group.addoption(
        "--benchmark-timer",
        action="store", type=loadtimer, default=default_timer,
        help="Timer to use when measuring time."
    )
    group.addoption(
        "--benchmark-warmup",
        action="store_true", default=False,
        help="Runs the benchmarks two times. Discards data from the first run."
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


class Default(namedtuple("Default", ["value"])):
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)

    def __int__(self):
        return self.value


class Benchmark(RunningStats):
    def __init__(self, name, disable_gc, timer, min_iterations, max_iterations, max_time, group=None):
        self._disable_gc = disable_gc
        self.name = name
        self.group = group
        self._timer = timer
        self._min_runs = min_iterations
        self._max_runs = max_iterations
        assert min_iterations <= max_iterations, (
           "Invalid configuration, min iterations need to be less than max "
           "iterations. You have %s min, %s max" % (min_iterations, max_iterations))
        self._max_time = float(max_time)
        self._stats = RunningStats()
        self._called = False
        self._start = None
        self._gcenabled = None
        self._overall_start = None
        super(Benchmark, self).__init__()

    def reset(self):
        super(Benchmark, self).reset()
        self._start = None
        self._gcenabled = None
        self._overall_start = None

    @property
    def done(self):
        if self._overall_start is None:
            self._overall_start = time.time()
        if self.runs < self._min_runs - 1:
            return False
        return time.time() - self._overall_start >= self._max_time or self.runs >= self._max_runs - 1

    # TODO: implement benchmark function wrapper (that adds the timers), as alternative to context manager
    # def __call__(self, function):
    #     pass

    def __enter__(self):
        self._gcenabled = gc.isenabled()
        if self._disable_gc:
            gc.disable()
        self._start = self._timer()
        return self

    def __exit__(self, *exc):
        end = self._timer()
        if self._gcenabled:
            gc.enable()
        self.update(end - self._start)


class BenchmarkSession(object):
    def __init__(self, config):
        max_iterations = config.getoption("benchmark_max_iterations")
        min_iterations = config.getoption("benchmark_min_iterations")
        if isinstance(max_iterations, Default):
            max_iterations = max(max_iterations.value, int(min_iterations))
        if isinstance(min_iterations, Default):
            min_iterations = min(min_iterations.value, int(max_iterations))
        if min_iterations > max_iterations:
            raise pytest.UsageError("Invalid arguments: --benchmark-min-iterations=%s cannot be greater than --benchmark-max-iterations=%s" % (min_iterations, max_iterations))
        self._options = dict(
            max_time=config.getoption("benchmark_max_time"),
            timer=config.getoption("benchmark_timer"),
            disable_gc=config.getoption("benchmark_disable_gc"),
            max_iterations=max_iterations,
            min_iterations=min_iterations,
        )
        self._warmup = config.getoption("benchmark_warmup")
        self._skip = config.getoption("benchmark_skip")
        self._only = config.getoption("benchmark_only")
        self._scale = config.getoption("benchmark_scale")
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
            benchmark = Benchmark(node.name, **dict(self._options, **options))
            self._benchmarks.append(benchmark)
            return benchmark

    def pytest_runtest_call(self, item):
        benchmark = hasattr(item, "funcargs") and item.funcargs.get("benchmark")
        if isinstance(benchmark, Benchmark):
            if self._warmup:
                while not benchmark.done:
                    item.runtest()
                benchmark.reset()
            while not benchmark.done:
                item.runtest()
        else:
            if self._only:
                pytest.skip("Skipping non-benchmark (--benchmark-only active).")
            else:
                item.runtest()

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
            tr.write_sep(
                "-",
                "benchmark{2}: {0} tests, {1.min_iterations} to {1.max_iterations} iterations,"
                " {1.max_time:f}s max time, timer: {3}".format(
                    len(benchmarks),
                    type("", (), self._options),
                    "" if group is None else " %r" % group,
                    timer_name,
                ),
                yellow=True
            )
            worst = {}
            best = {}
            for prop in ("min", "max", "mean", "stddev", "runs"):
                worst[prop] = max(getattr(benchmark, prop) for benchmark in benchmarks)
            for prop in ("min", "max", "mean", "stddev"):
                best[prop] = min(getattr(benchmark, prop) for benchmark in benchmarks)

            overall_min = best[self._scale]
            if overall_min < 0.000001:
                unit, adjustment = "n", 1e9
            elif overall_min < 0.001:
                unit, adjustment = "u", 1e6
            elif overall_min < 1:
                unit, adjustment = "m", 1e3
            else:
                unit, adjustment = "", 1.
            labels = {
                "name": "Name (time in %ss)" % unit,
                "min": "Min",
                "max": "Max",
                "mean": "Mean",
                "stddev": "StdDev",
                "runs": "Iterations",
            }
            widths = {
                "name": 3 + max(len(labels["name"]), max(len(benchmark.name) for benchmark in benchmarks)),
                "runs": 2 + max(len(labels["runs"]), len(str(worst["runs"]))),
            }
            for prop in ("min", "max", "mean", "stddev"):
                widths[prop] = 2 + max(len(labels[prop]), max(
                    len("{0:.4f}".format(getattr(benchmark, prop) * adjustment))
                    for benchmark in benchmarks
                ))
            tr.write_line(labels["name"].ljust(widths["name"]) + "".join(
                labels[prop].rjust(widths[prop])
                for prop in ("min", "max", "mean", "stddev", "runs")
            ))
            tr.write_line("-" * sum(widths.values()))

            for benchmark in benchmarks:
                tr.write(benchmark.name.ljust(widths["name"]))
                for prop in ("min", "max", "mean", "stddev"):
                    value = getattr(benchmark, prop)
                    tr.write(
                        "{0:>{1}.4f}".format(value * adjustment, widths[prop]),
                        green=value == best[prop],
                        red=value == worst[prop],
                        bold=True,
                    )
                tr.write("{0:>{1}}".format(benchmark.runs, widths["runs"]))
                tr.write("\n")

            tr.write_line("-" * sum(widths.values()))
            tr.write_line("")


def pytest_runtest_setup(item):
    benchmark = item.get_marker("benchmark")
    if benchmark:
        if benchmark.args:
            raise ValueError("benchmark mark can't have positional arguments.")
        for name in benchmark.kwargs:
            if name not in ("max_time", "min_iterations", "max_iterations", "timer", "group", "disable_gc"):
                raise ValueError("benchmark mark can't have %r keyword argument." % name)


def pytest_configure(config):
    config.addinivalue_line("markers", "benchmark: mark a test with custom benchmark settings.")
    config.pluginmanager.register(BenchmarkSession(config), "pytest-benchmark")
