"""
Just to make sure the plugin doesn't choke on doctests::

    >>> print('Yay, doctests!')
    Yay, doctests!

"""
import time
from functools import partial

import pytest


def test_fast(benchmark):
    @benchmark
    def result():
        return time.sleep(0.000001)
    assert result is None


def test_slow(benchmark):
    assert benchmark(partial(time.sleep, 0.001)) is None


def test_slower(benchmark):
    benchmark(lambda: time.sleep(0.01))


@pytest.mark.benchmark(min_rounds=2, timer=time.time)
def test_xfast(benchmark):
    benchmark(str)


def test_fast(benchmark):
    benchmark(int)
