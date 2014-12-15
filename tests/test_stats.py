from pytest_benchmark.stats import RunningStats


def test_1():
    stats = RunningStats()
    for i in 4., 36., 45., 50., 75.:
        stats.update(i)
    print(stats)
    fail

def test_2():
    stats = RunningStats()

    stats.update(17.0)
    stats.update(19.0)
    stats.update(24.0)
    print(stats)
    fail
