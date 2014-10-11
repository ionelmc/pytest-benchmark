from __future__ import division

import gc
import sys
import timeit

import pytest

from .stats import RunningStats


def loadtimer(string):
    if '.' not in string:
        raise ValueError("Value for benchmark-timer must be in dotted form. Eg: 'module.attr'.")
    mod, attr = string.rsplit('.', 1)
    __import__(mod)
    mod = sys.modules[mod]
    return getattr(mod, attr)


def pytest_addoption(parser):
    group = parser.getgroup("benchmark")
    group.addoption(
        '--benchmark-max-time',
        action="store", type=float, default=0.5,
        help="Maximum time to spend in a benchmark."
    )
    group.addoption(
        '--benchmark-max-iterations',
        action="store", type=int, default=5000,
        help="Maximum iterations to do."
    )
    group.addoption(
        '--benchmark-min-iterations',
        action="store", type=int, default=5,
        help="Minium iterations, even if total time would exceed `max-time`."
    )
    group.addoption(
        '--benchmark-timer',
        action="store", type=loadtimer, default=timeit.default_timer,
        help="Timer to use when measuring time."
    )
    group.addoption(
        '--benchmark-disable-gc',
        action="store_true", default=False,
        help="Disable GC during benchmarks."
    )


class Benchmark(RunningStats):
    def __init__(self, name, disable_gc, timer, min_iterations, max_iterations, max_time):
        self._disable_gc = disable_gc
        self.name = name
        self._timer = timer
        self._min_runs = min_iterations
        self._max_runs = max(max_iterations, max_iterations)
        #assert min_iterations <= max_iterations, (
        #    "Invalid configuration, min iterations need to be less than max "
        #    "iterations. You have %s min, %s max" % (min_iterations, max_iterations))
        self._max_time = max_time
        self._stats = RunningStats()
        self._called = False
        self._start = None
        self._gcenabled = None
        super(Benchmark, self).__init__()

    @property
    def done(self):
        return not (self.runs < self._min_runs or self.total < self._max_time) or self.runs >= self._max_runs

    def __call__(self, function):
        # TODO: make decorator
        pass

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
        self._options = dict(
            max_time=config.getoption('benchmark_max_time'),
            max_iterations=config.getoption('benchmark_max_iterations'),
            min_iterations=config.getoption('benchmark_min_iterations'),
            timer=config.getoption('benchmark_timer'),
            disable_gc=config.getoption('benchmark_disable_gc'),
        )
        self._benchmarks = []

    @pytest.fixture(scope="function")
    def benchmark(self, request):
        node = request.node
        marker = node.get_marker('benchmark')
        options = marker.kwargs if marker else {}
        benchmark = Benchmark(node.name, **dict(self._options, **options))
        self._benchmarks.append(benchmark)
        return benchmark

    def pytest_terminal_summary(self, terminalreporter):
        if not self._benchmarks:
            return
        tr = terminalreporter
        tr.write_sep('-',
                     'benchmark: {0} tests, {1.min_iterations} to {1.max_iterations} iterations,'
                     ' {1.max_time}s max time'.format(len(self._benchmarks), type('', (), self._options)),
                     yellow=True)
        worst = {}
        best = {}
        for prop in ('min', 'max', 'avg', 'mean', 'stddev', 'runs'):
            worst[prop] = max(getattr(benchmark, prop) for benchmark in self._benchmarks)
        for prop in ('min', 'max', 'avg', 'mean', 'stddev'):
            best[prop] = min(getattr(benchmark, prop) for benchmark in self._benchmarks)
        widths = {
            'name': max(20, max(len(benchmark.name) for benchmark in self._benchmarks)),
            'runs': len(str(worst['runs'])),
        }

        overall_min = max(best.values())
        if overall_min < 0.000001:
            unit, adjustment = 'n', 1000000000
        if overall_min < 0.001:
            unit, adjustment = 'u', 1000000
        elif overall_min < 1:
            unit, adjustment = 'm', 1000
        else:
            unit, adjustment = '', 1

        for prop in ('min', 'max', 'avg', 'mean', 'stddev'):
            widths[prop] = min(6, max(
                len("{0:.3f}".format(getattr(benchmark, prop) * adjustment))
                for benchmark in self._benchmarks
            ))
        tr.write_line("{0:<{1}}   {2:>{3}}  {4:>{5}}  {6:>{7}}  {8:>{9}}  {10:>{11}}  {12:>{13}}".format(
            "Name (time in %ss)" % unit, widths['name'],
            'Min', widths['min'] + 3,
            'Max', widths['max'] + 3,
            'Avg', widths['avg'] + 3,
            'Mean', widths['mean'] + 3,
            'StdDev', widths['stddev'] + 3,
            'Iterations', widths['runs'] + 3,
        ))
        tr.write_line("-" * sum(widths.values(), 5 + len(widths) * 4))

        for benchmark in self._benchmarks:
            tr.write("{0:<{1}} ".format(benchmark.name, widths['name']))
            for prop in ('min', 'max', 'avg', 'mean', 'stddev'):
                value = getattr(benchmark, prop)
                tr.write(
                    "  {0:>{1}.3f}".format(value * adjustment, widths[prop] + 3),
                    green=value == best[prop],
                    red=value == worst[prop],
                    bold=True,
                )
            tr.write(
                "  {0:>{1}}".format(benchmark.runs, widths['runs'] + 5),
            )
            tr.write('\n')


def pytest_runtest_call(item):
    benchmark = hasattr(item, 'funcargs') and item.funcargs.get('benchmark')
    if isinstance(benchmark, Benchmark):
        while not benchmark.done:
            item.runtest()
    else:
        item.runtest()


def pytest_runtest_setup(item):
    benchmark = item.get_marker('benchmark')
    if benchmark:
        if benchmark.args:
            raise ValueError("benchmark mark can't have positional arguments.")
        for name in benchmark.kwargs:
            if name not in ('max_time', 'min_iterations', 'max_iterations', 'timer'):
                raise ValueError("benchmark mark can't have %r keyword argument." % name)


def pytest_configure(config):
    config.addinivalue_line("markers", "benchmark: mark a test with custom benchmark settings.")
    config.pluginmanager.register(BenchmarkSession(config), 'pytest-benchmark')
