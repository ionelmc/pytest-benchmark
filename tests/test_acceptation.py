"""
Sometimes it can be useful to modify the statistics to take into account
something that the benchmark cannot natively (a benchmark on a function which
takes care of a hundred files, while wishing to have the OPS per file)
"""

import pytest

from pytest_benchmark.fixture import BenchmarkFixture
from pytest_benchmark.stats import Stats

# List of modifiable attributes of the statistics attribute of the benchmark fixture
list_modifiable_statistics_attributes = [
    'mean',
    'stddev',
    'stddev_outliers',
    'median',
    'min',
    'max',
    'q1',
    'q3',
    'iqr',
    'iqr_outliers',
    'ld15iqr',
    'hd15iqr',
    'outliers',
    'ops',
    'total',
]

# List of unmodifiable attributes of the statistics attribute of the benchmark fixture
list_unmodifiable_statistics_attributes = [
    'rounds',
]


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


@pytest.mark.parametrize('attribute', list_modifiable_statistics_attributes)
def test_benchmark_stats_can_be_modified(benchmark: BenchmarkFixture, attribute: str):
    """ Test to ensure that attributes of statistics can be modified. """

    # Run a benchmark to have some statistics
    benchmark.pedantic(lambda: 1 + 1, rounds=1, iterations=1, warmup_rounds=0)

    # Check that the attribute exists
    assert hasattr(benchmark.statistics, attribute)

    # Check that the value is not None
    old_value = benchmark.statistics.__getattribute__(attribute)

    # Can matter whether it's a string or a number it will work
    benchmark.statistics.__setattr__(attribute, old_value * 2)  # like "benchmark.statistics.mean *= 2"

    # Check that the value has been modified
    assert benchmark.statistics.__getattribute__(attribute) == old_value * 2


@pytest.mark.parametrize('attribute', list_unmodifiable_statistics_attributes)
def test_benchmark_stats_cant_be_modified(benchmark: BenchmarkFixture, attribute: str):
    """ Test to ensure that attributes of statistics can't be modified. """

    # Run a benchmark to have some statistics
    benchmark.pedantic(lambda: 1 + 1, rounds=1, iterations=1, warmup_rounds=0)

    # Check that the attribute exists
    assert hasattr(benchmark.statistics, attribute)

    # Check that the value is not None
    old_value = benchmark.statistics.__getattribute__(attribute)

    # AttributeError
    with pytest.raises(AttributeError):
        benchmark.statistics.__setattr__(attribute, old_value * 2)  # like "benchmark.statistics.mean *= 2"


def test_benchmark_fixture_access_stats(benchmark: BenchmarkFixture):
    """ Test to ensure that the benchmark fixture has a statistics attribute. """

    # Delete warning "Benchmark fixture was not used at all in this test!"
    benchmark.pedantic(lambda: 1 + 1, rounds=1, iterations=1, warmup_rounds=0)

    assert hasattr(benchmark, 'statistics')
    assert isinstance(benchmark.statistics, Stats)
