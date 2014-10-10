from __future__ import division
import gc
import timeit
import pytest
import sys
import collections
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
        action="store", type=int, default=10000,
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


class Benchmark(object):
    def __init__(self, name, disable_gc, timer, min_iterations, max_iterations, max_time):
        print((name, disable_gc, timer, min_iterations, max_time))
        self._disable_gc = disable_gc
        self._name = name
        self._timer = timer
        self._min_iterations = min_iterations
        self._max_iterations = max_iterations
        self._max_time = max_time
        self._stats = RunningStats()
        self._called = False
        self._start = None
        self._gcenabled = None

    @property
    def done(self):
        return not (self._stats.runs < self._min_iterations or self._stats.total < self._max_time) or self._stats.runs >= self._max_iterations

    #def __call__(self, function):
    #    use_decorator

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
        self._stats.update(end - self._start)


class BenchmarkSession(object):
    def __init__(self, config):
        self.options = dict(
            max_time=config.getoption('benchmark_max_time'),
            max_iterations=config.getoption('benchmark_max_iterations'),
            min_iterations=config.getoption('benchmark_min_iterations'),
            timer=config.getoption('benchmark_timer'),
            disable_gc=config.getoption('benchmark_disable_gc'),
        )
        self.benchmarks = []

    def new(self, name, **kwargs):
        benchmark = Benchmark(name, **dict(self.options, **kwargs))
        self.benchmarks.append(benchmark)
        return benchmark


@pytest.fixture(scope="function")
def benchmark(request, _benchmark_session):
    benchmark = request.node.keywords.get('benchmark')
    # TODO: use `node.get_marker`
    options = benchmark.kwargs if benchmark else {}
    return _benchmark_session.new(request.node.name, **options)


@pytest.fixture(scope="session")
def _benchmark_session(request):
    return BenchmarkSession(request.config)


def pytest_runtest_call(item):
    benchmark = item.funcargs.get('benchmark')
    if isinstance(benchmark, Benchmark):
        while not benchmark.done:
            item.runtest()

        print(benchmark._stats)
    else:
        item.runtest()

def pytest_report_teststatus(report):
    """ adapted from
    https://bitbucket.org/hpk42/pytest/src/a5e7a5fa3c7e/_pytest/skipping.py#cl-170
    """
    if report.when in ("call"):
        if hasattr(report, "rerun") and report.rerun > 0:
            if report.outcome == "failed":
                return "failed", "F", "FAILED"
            if report.outcome == "passed":
                return "rerun", "R", "RERUN"


def pytest_terminal_summary(terminalreporter):
    """ adapted from
    https://bitbucket.org/hpk42/pytest/src/a5e7a5fa3c7e/_pytest/skipping.py#cl-179
    """
    tr = terminalreporter
    if not tr.reportchars:
        return

    lines = []
    for char in tr.reportchars:
        if char in "rR":
            show_rerun(terminalreporter, lines)

    if lines:
        tr._tw.sep("=", "rerun test summary info")
        for line in lines:
            tr._tw.line(line)


def pytest_configure(config):
    config.addinivalue_line("markers", "benchmark: mark a test with custom benchmark settings.")


def pytest_runtest_setup(item):
    benchmark = item.get_marker('benchmark')
    if benchmark:
        if benchmark.args:
            raise ValueError("benchmark mark can't have positional arguments.")
        for name in benchmark.kwargs:
            if name not in ('max_time', 'min_iterations', 'timer'):
                raise ValueError("benchmark mark can't have %r keyword argument." % name)
