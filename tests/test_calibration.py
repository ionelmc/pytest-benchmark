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


def timer(ratio, step, additive):
    t = 0
    slowmode = False
    while 1:
        if additive:
            slowmode |= bool((yield t))
        else:
            slowmode = bool((yield t))
        if slowmode:
            t += step * ratio
        else:
            t += step


@pytest.mark.parametrize("minimum", [1, 0.01, 0.000000001, 0.0000000001, 1.000000000000001])
@pytest.mark.parametrize("skew_ratio", [0, 1, -1])
@pytest.mark.parametrize("additive", [True, False])
@pytest.mark.benchmark(max_time=0, min_rounds=1, calibration_precision=100)
def test_calibrate_stuck(benchmark, minimum, additive, skew_ratio):
    # if skew_ratio:
    #     ratio += skew_ratio * SKEW
    if skew_ratio > 0:
        ratio = 50 * 1.000000000000001
    elif skew_ratio < 0:
        ratio = 50 / 1.000000000000001
    else:
        ratio = 50
    t = timer(ratio, minimum, additive)
    benchmark._timer = partial(next, t)
    benchmark._min_time = minimum
    benchmark(t.send, True)

