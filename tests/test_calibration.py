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


MIN = 0.0000001


def Timer():
    t = 0
    slowmode = False
    c = 0
    while 1:
        slowmode |= bool((yield t))
        if slowmode:
            import sys
            sys.stdout.write('[%s]' % c)

            if 0:
                t += 74.9
            else:
                t += MIN * 100.1
            c += 1
        else:
            t += MIN


timer = Timer()


@pytest.mark.benchmark(max_time=MIN, min_rounds=1, min_time=MIN, timer=timer.__next__)
def test_calibrate_very_slow(benchmark):
    benchmark._get_precision(benchmark._timer)
    benchmark(timer.send, True)
