from pytest_benchmark.stats import RunningStats


def test_1():
    stats = RunningStats()
    for i in 4., 36., 45., 50., 75.:
        stats.update(i)
    assert stats.mean == 42.
    assert stats.min == 4.
    assert stats.max == 75.
    assert stats.stddev == 25.700194551792794
    assert stats.runs == 5
    assert stats.total == 210.



def test_2():
    stats = RunningStats()
    stats.update(17.)
    stats.update(19.)
    stats.update(24.)
    assert stats.mean == 20.
    assert stats.min == 17.
    assert stats.max == 24.
    assert stats.stddev == 3.605551275463989
    assert stats.runs == 3
    assert stats.total == 60.
