from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import cProfile
    import pstats
    from collections.abc import Hashable
    from typing import Any
    from typing import assert_type
    from typing import type_check_only

    from pytest_benchmark.fixture import BenchmarkFixture
    from pytest_benchmark.stats import Metadata
    from pytest_benchmark.stats import _FlatMetadataDict  # type: ignore
    from pytest_benchmark.stats import _MetadataDict  # type: ignore

    @type_check_only
    def test_benchmarkfixture_hints(benchmark: BenchmarkFixture):
        # Attributes
        assert_type(benchmark.name, str)
        assert_type(benchmark.fullname, str)
        assert_type(benchmark.disabled, bool)
        assert_type(benchmark.param, str | None)
        assert_type(benchmark.params, dict[str, Any] | None)
        assert_type(benchmark.group, str | None)
        assert_type(benchmark.has_error, bool)
        assert_type(benchmark.extra_info, dict[Hashable, Any])
        assert_type(benchmark.skipped, bool)
        assert_type(benchmark.cprofile, cProfile.Profile)
        assert_type(benchmark.cprofile_loops, int | None)
        assert_type(benchmark.cprofile_dump, str | None)
        assert_type(benchmark.cprofile_stats, pstats.Stats | None)
        assert_type(benchmark.stats, Metadata | None)

        if benchmark.stats:
            assert_type(benchmark.stats.as_dict(), _MetadataDict | _FlatMetadataDict)

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
        benchmark.pedantic(
            len,
            {},  # type: ignore[call-overload]
            (),  # type: ignore[call-overload]
        )

        # Pass `args`/`kwargs` and `setup` (Should show Type Error)
        benchmark.pedantic(
            len,
            args=(),
            kwargs={},
            setup=lambda: ((), {}),  # type: ignore[call-overload]
        )
