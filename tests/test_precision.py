"""
Tests for the ``--benchmark-precision`` stopping rule.

Most tests call ``BenchmarkFixture._run_until_precise`` directly with a fake runner
so the statistics are deterministic.
"""

import pytest


class FakeStats:
    def __init__(self):
        self.data = []

    def update(self, duration):
        self.data.append(duration)


def make_runner(values):
    it = iter(values)
    return lambda loops_range: next(it)


def configure(benchmark, precision, min_rounds=5, confidence=0.99):
    benchmark._mode = 'benchmark(...)'  # mark the fixture as used since we bypass __call__
    benchmark._min_rounds = min_rounds
    benchmark._precision = precision
    benchmark._confidence = confidence
    return benchmark


def test_zero_variance_stops_at_min_rounds(benchmark):
    # Identical samples have zero margin of error, so it stops exactly at min_rounds.
    configure(benchmark, precision=0.01, min_rounds=5)
    stats = FakeStats()
    benchmark._run_until_precise(make_runner([1.0] * 100), range(1), stats, 50)
    assert len(stats.data) == 5


def test_never_precise_runs_to_cap(benchmark):
    # Alternating samples never reach the tight margin, so it runs to the max_rounds cap.
    configure(benchmark, precision=0.0001, min_rounds=2)
    stats = FakeStats()
    benchmark._run_until_precise(make_runner([1.0, 5.0] * 100), range(1), stats, 20)
    assert len(stats.data) == 20


def test_stops_early_when_precise_enough(benchmark):
    # Small but nonzero variance: stops somewhere between min_rounds and the cap.
    configure(benchmark, precision=0.05, min_rounds=3)
    stats = FakeStats()
    samples = [0.99, 1.01] * 500
    benchmark._run_until_precise(make_runner(samples), range(1), stats, 1000)
    assert 3 <= len(stats.data) < 1000


@pytest.mark.benchmark(precision=0.05, max_time=2.0, min_rounds=3)
def test_precision_marker_end_to_end(benchmark):
    # Full path: marker options through the fixture to the adaptive loop.
    benchmark(lambda: sum(range(50)))
    assert benchmark.stats.stats.rounds >= 3
