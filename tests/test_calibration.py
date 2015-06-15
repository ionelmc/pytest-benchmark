from functools import partial
import time

import pytest


def slow_warmup():
    x = 0
    for _ in range(1000):
        x *= 1


@pytest.mark.benchmark(warmup=True, warmup_iterations=10 ** 8, max_time=10)
def test_calibrate(benchmark):
    benchmark(slow_warmup)


@pytest.mark.benchmark(warmup=True, warmup_iterations=10 ** 8, max_time=10)
def test_calibrate_fast(benchmark):
    benchmark(lambda: [int] * 100)


@pytest.mark.benchmark(warmup=True, warmup_iterations=10 ** 8, max_time=10)
def test_calibrate_xfast(benchmark):
    benchmark(lambda: None)


@pytest.mark.benchmark(warmup=True, warmup_iterations=10 ** 8, max_time=10)
def test_calibrate_slow(benchmark):
    benchmark(partial(time.sleep, 0.00001))
