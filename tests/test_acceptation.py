""" Testing to ensure that __init__ makes typing import simple and accessible to IDEs. """
from pytest_benchmark.fixture import BenchmarkFixture
from pytest_benchmark.stats import Stats


def test_import_benchmark_fixture():
    """ Test to ensure that __init__ makes importing for typing simple and accessible to IDEs. """
    Module = None

    # Check that the import is successful
    try:
        from pytest_benchmark import BenchmarkFixture as Module
    except ImportError:
        pass
    finally:
        assert Module is not None


def test_import_stats():
    """ Test to ensure that __init__ makes importing for typing simple and accessible to IDEs. """
    Module = None

    # Check that the import is successful
    try:
        from pytest_benchmark import Stats as Module
    except ImportError:
        pass
    finally:
        assert Module is not None


def test_benchmark_fixture_access_stats(benchmark: BenchmarkFixture):
    """
    Test to ensure that __init__ makes accessing stats simple and accessible to IDEs.

    Sometimes it can be useful to modify the statistics to take into account
    something that the benchmark cannot natively (a benchmark on a function which
    takes care of a hundred files, while wishing to have the OPS per file)
    """

    benchmark.pedantic(lambda: 1 + 1, rounds=1, iterations=1, warmup_rounds=0)

    assert hasattr(benchmark, 'statistics')
    assert isinstance(benchmark.statistics, Stats)

    old_ops = benchmark.statistics.ops
    benchmark.statistics.ops *= 2
    assert benchmark.statistics.ops == old_ops * 2

