"""
Just to make sure the plugin doesn't choke on doctests::

    >>> print('Yay, doctests!')
    Yay, doctests!

"""

import sys  # noqa
import time
from functools import partial

import pytest

from pytest_benchmark.fixture import BenchmarkFixture


@pytest.mark.skipif('sys.platform == "win32"')
def test_fast(benchmark: BenchmarkFixture) -> None:
    @benchmark
    def result():
        return time.sleep(0.000001)

    assert result is None

    if not benchmark.disabled:
        assert benchmark.stats.stats.min >= 0.000001


def test_slow(benchmark: BenchmarkFixture) -> None:
    assert benchmark(partial(time.sleep, 0.001)) is None


def test_slower(benchmark: BenchmarkFixture) -> None:
    benchmark(lambda: time.sleep(0.01))


@pytest.mark.benchmark(min_rounds=2, timer=time.time, max_time=0.01)
def test_xfast(benchmark: BenchmarkFixture) -> None:
    benchmark(str)


@pytest.fixture(params=range(5))
def foo(request: pytest.FixtureRequest) -> int:
    assert isinstance(request.param, int)
    return request.param


@pytest.mark.skipif('sys.platform == "win32"')
def test_parametrized(benchmark: BenchmarkFixture, foo: int) -> None:
    benchmark(time.sleep, 0.00001)
    if benchmark.enabled:
        assert benchmark.stats.stats.min >= 0.00001
