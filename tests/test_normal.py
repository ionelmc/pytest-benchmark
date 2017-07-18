"""
Just to make sure the plugin doesn't choke on doctests::

    >>> print('Yay, doctests!')
    Yay, doctests!

"""
import sys
import time
from functools import partial

import pytest


@pytest.mark.skipif('sys.platform == "win32"')
def test_fast(benchmark):
    @benchmark
    def result():
        return time.sleep(0.000001)
    assert result is None

    if not benchmark.disabled:
        assert benchmark.stats.stats.min >= 0.000001


def test_slow(benchmark):
    assert benchmark(partial(time.sleep, 0.001)) is None


def test_slower(benchmark):
    benchmark(lambda: time.sleep(0.01))


# @pytest.mark.benchmark(min_rounds=2, timer=time.time, max_time=0.01)
# def test_xfast(benchmark):
#     benchmark(str)


@pytest.fixture(params=range(5))
def foo(request):
    return request.param


@pytest.mark.skipif('sys.platform == "win32"')
def test_parametrized(benchmark, foo):
    benchmark(time.sleep, 0.00001)
    if benchmark.enabled:
        assert benchmark.stats.stats.min >= 0.00001
