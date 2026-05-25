import cProfile
from typing import Any
from typing import assert_type

import pytest
from src.pytest_benchmark.fixture import BenchmarkFixture

pytest.mark.skip('No Run (Type Check)')


def test_benchmarkfixture_hints(benchmark: BenchmarkFixture):
    # Attributes
    assert_type(benchmark.name, str)
    assert_type(benchmark.fullname, str)
    assert_type(benchmark.disabled, bool)
    assert_type(benchmark.param, str | None)
    assert_type(benchmark.params, tuple[str, ...] | None)
    assert_type(benchmark.group, str | None)
    assert_type(benchmark.has_error, bool)
    assert_type(benchmark.extra_info, dict[str, Any])
    assert_type(benchmark.skipped, bool)
    assert_type(benchmark.cprofile, cProfile.Profile)
    assert_type(benchmark.cprofile_loops, int | None)
    assert_type(benchmark.cprofile_dump, str | None)
    assert_type(benchmark.cprofile_stats, dict[Any, Any] | None)
    assert_type(benchmark.stats, dict[Any, Any] | None)

    # Properties
    assert_type(benchmark.enabled, bool)

    # Methods

    # Test that types are maintained when __call__ ing the fixture
    assert_type(benchmark.__call__(map, len, 'a'), map[int])
    assert_type(benchmark.__call__(len, []), int)
    assert_type(benchmark.__call__(repr, []), str)

    # `args`/`kwargs`
    assert_type(benchmark.pedantic(len, args=([],)), int)
    assert_type(benchmark.pedantic(len, kwargs={}), int)
    assert_type(benchmark.pedantic(len, args=(), kwargs={}), int)
    assert_type(benchmark.pedantic(len, (), {}), int)
    assert_type(benchmark.pedantic(len, kwargs={}, rounds=10, teardown=print), int)

    # `setup`
    assert_type(benchmark.pedantic(len, setup=lambda: ((), {})), int)
    assert_type(benchmark.pedantic(len, setup=lambda: (([1, 2, 3],), {})), int)

    # Reverse Positionals (Should show Type Error)
    benchmark.pedantic(len, {}, ())

    # Pass `args`/`kwargs` and `setup` (Should show Type Error)
    benchmark.pedantic(len, args=(), setup=lambda: ((), {}))
