import json
import platform

import pytest

pytest_plugins = ('pytester',)
platform  # noqa: B018


def test_help(testdir):
    result = testdir.runpytest_subprocess('--help')
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            'benchmark:',
            '  --benchmark-min-time=SECONDS',
            "                        *Default: '0.000005'",
            '  --benchmark-max-time=SECONDS',
            "                        *Default: '1.0'",
            '  --benchmark-min-rounds=NUM',
            '                        *Default: 5',
            '  --benchmark-timer=FUNC',
            '  --benchmark-calibration-precision=NUM',
            '                        *Default: 10',
            '  --benchmark-warmup=[KIND]',
            '  --benchmark-warmup-iterations=NUM',
            '                        *Default: 100000',
            '  --benchmark-disable-gc',
            '  --benchmark-skip      *',
            '  --benchmark-only      *',
            '  --benchmark-save=NAME',
            '  --benchmark-autosave  *',
            '  --benchmark-save-data',
            '  --benchmark-json=PATH',
            '  --benchmark-compare=[NUM|_ID]',
            '  --benchmark-compare-fail=EXPR?[[]EXPR?...[]]',
            '  --benchmark-cprofile=COLUMN',
            '  --benchmark-storage=URI',
            "                        *Default: 'file://./.benchmarks'.",
            '  --benchmark-verbose   *',
            '  --benchmark-sort=COL  *',
            '  --benchmark-group-by=LABEL',
            "                        *Default: 'group'",
            '  --benchmark-columns=LABELS',
            '  --benchmark-histogram=[FILENAME-PREFIX]',
            '*',
        ]
    )


def test_groups(testdir):
    test = testdir.makepyfile(
        '''"""
    >>> print('Yay, doctests!')
    Yay, doctests!
"""
import time
import pytest

def test_fast(benchmark):
    benchmark(lambda: time.sleep(0.000001))
    assert 1 == 1

def test_slow(benchmark):
    benchmark(lambda: time.sleep(0.001))
    assert 1 == 1

@pytest.mark.benchmark(group="A")
def test_slower(benchmark):
    benchmark(lambda: time.sleep(0.01))
    assert 1 == 1

@pytest.mark.benchmark(group="A", warmup=True)
def test_xfast(benchmark):
    benchmark(lambda: None)
    assert 1 == 1
'''
    )
    result = testdir.runpytest_subprocess('-vv', '--doctest-modules', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items',
            '*',
            'test_groups.py::*test_groups PASSED*',
            'test_groups.py::test_fast PASSED*',
            'test_groups.py::test_slow PASSED*',
            'test_groups.py::test_slower PASSED*',
            'test_groups.py::test_xfast PASSED*',
            '*',
            '* benchmark: 2 tests *',
            '*',
            "* benchmark 'A': 2 tests *",
            '*',
            '*====== 5 passed * ======*',
        ]
    )


SIMPLE_TEST = '''
"""
    >>> print('Yay, doctests!')
    Yay, doctests!
"""
import time
import pytest

def test_fast(benchmark):
    @benchmark
    def result():
        return time.sleep(0.000001)
    assert result == None

def test_slow(benchmark):
    benchmark(lambda: time.sleep(0.1))
    assert 1 == 1
'''

FIXTURES_ALSO_SKIPPED_TEST = '''
import pytest

@pytest.fixture
def dep():
    print("""
dep created""")

def test_normal(dep):
    pass

def test_bench(benchmark):
    benchmark.pedantic(lambda: None)
'''

GROUPING_TEST = """
import pytest

@pytest.mark.parametrize("foo", range(2))
@pytest.mark.benchmark(group="A")
def test_a(benchmark, foo):
    benchmark(str)

@pytest.mark.parametrize("foo", range(2))
@pytest.mark.benchmark(group="B")
def test_b(benchmark, foo):
    benchmark(int)
"""

GROUPING_PARAMS_TEST = """
import pytest

@pytest.mark.parametrize("bar", ["bar1", "bar2"])
@pytest.mark.parametrize("foo", ["foo1", "foo2"])
@pytest.mark.benchmark(group="A")
def test_a(benchmark, foo, bar):
    benchmark(str)


@pytest.mark.parametrize("bar", ["bar1", "bar2"])
@pytest.mark.parametrize("foo", ["foo1", "foo2"])
@pytest.mark.benchmark(group="B")
def test_b(benchmark, foo, bar):
    benchmark(int)
"""


def test_group_by_name(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'name', test_x, test_y)
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            '*',
            '*',
            '*',
            "* benchmark 'test_a[[]0[]]': 2 tests *",
            'Name (time in ?s)     *',
            '----------------------*',
            'test_a[[]0[]]             *',
            'test_a[[]0[]]             *',
            '----------------------*',
            '*',
            "* benchmark 'test_a[[]1[]]': 2 tests *",
            'Name (time in ?s)     *',
            '----------------------*',
            'test_a[[]1[]]             *',
            'test_a[[]1[]]             *',
            '----------------------*',
            '*',
            "* benchmark 'test_b[[]0[]]': 2 tests *",
            'Name (time in ?s)     *',
            '----------------------*',
            'test_b[[]0[]]             *',
            'test_b[[]0[]]             *',
            '----------------------*',
            '*',
            "* benchmark 'test_b[[]1[]]': 2 tests *",
            'Name (time in ?s)     *',
            '----------------------*',
            'test_b[[]1[]]             *',
            'test_b[[]1[]]             *',
            '----------------------*',
        ]
    )


def test_group_by_func(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'func', test_x, test_y)
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            '*',
            '*',
            "* benchmark 'test_a': 4 tests *",
            'Name (time in ?s)     *',
            '----------------------*',
            'test_a[[]*[]]             *',
            'test_a[[]*[]]             *',
            'test_a[[]*[]]             *',
            'test_a[[]*[]]             *',
            '----------------------*',
            '*',
            "* benchmark 'test_b': 4 tests *",
            'Name (time in ?s)     *',
            '----------------------*',
            'test_b[[]*[]]             *',
            'test_b[[]*[]]             *',
            'test_b[[]*[]]             *',
            'test_b[[]*[]]             *',
            '----------------------*',
            '*',
            '*',
            '============* 8 passed * ============*',
        ]
    )


def test_group_by_fullfunc(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'fullfunc', test_x, test_y)
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            '*',
            '*',
            '*',
            "* benchmark 'test_x.py::test_a': 2 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_a[[]*[]]         *',
            'test_a[[]*[]]         *',
            '------------------*',
            '',
            "* benchmark 'test_x.py::test_b': 2 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_b[[]*[]]         *',
            'test_b[[]*[]]         *',
            '------------------*',
            '',
            "* benchmark 'test_y.py::test_a': 2 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_a[[]*[]]         *',
            'test_a[[]*[]]         *',
            '------------------*',
            '',
            "* benchmark 'test_y.py::test_b': 2 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_b[[]*[]]         *',
            'test_b[[]*[]]         *',
            '------------------*',
            '',
            'Legend:',
            '  Outliers: 1 Standard Deviation from M*',
            '============* 8 passed * ============*',
        ]
    )


def test_group_by_param_all(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'param', test_x, test_y)
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            '*',
            '*',
            '*',
            "* benchmark '0': 4 tests *",
            'Name (time in ?s)  *',
            '-------------------*',
            'test_*[[]0[]]          *',
            'test_*[[]0[]]          *',
            'test_*[[]0[]]          *',
            'test_*[[]0[]]          *',
            '-------------------*',
            '',
            "* benchmark '1': 4 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_*[[]1[]]         *',
            'test_*[[]1[]]         *',
            'test_*[[]1[]]         *',
            'test_*[[]1[]]         *',
            '------------------*',
            '',
            'Legend:',
            '  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd ' 'Quartile.',
            '============* 8 passed * ============*',
        ]
    )


def test_group_by_param_select(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_PARAMS_TEST)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--benchmark-group-by', 'param:foo', '--benchmark-sort', 'fullname', test_x
    )
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            '*',
            '*',
            '*',
            "* benchmark 'foo=foo1': 4 tests *",
            'Name (time in ?s)  *',
            '-------------------*',
            'test_a[[]foo1-bar1[]]    *',
            'test_a[[]foo1-bar2[]]    *',
            'test_b[[]foo1-bar1[]]    *',
            'test_b[[]foo1-bar2[]]    *',
            '-------------------*',
            '',
            "* benchmark 'foo=foo2': 4 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_a[[]foo2-bar1[]]    *',
            'test_a[[]foo2-bar2[]]    *',
            'test_b[[]foo2-bar1[]]    *',
            'test_b[[]foo2-bar2[]]    *',
            '------------------*',
            '',
            'Legend:',
            '  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd ' 'Quartile.',
            '============* 8 passed * ============*',
        ]
    )


def test_group_by_param_select_multiple(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_PARAMS_TEST)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--benchmark-group-by', 'param:foo,param:bar', '--benchmark-sort', 'fullname', test_x
    )
    result.stdout.fnmatch_lines(
        [
            '*',
            '*',
            '*',
            '*',
            '*',
            "* benchmark 'foo=foo1 bar=bar1': 2 tests *",
            'Name (time in ?s)  *',
            '-------------------*',
            'test_a[[]foo1-bar1[]]    *',
            'test_b[[]foo1-bar1[]]    *',
            '-------------------*',
            '',
            "* benchmark 'foo=foo1 bar=bar2': 2 tests *",
            'Name (time in ?s)  *',
            '-------------------*',
            'test_a[[]foo1-bar2[]]    *',
            'test_b[[]foo1-bar2[]]    *',
            '-------------------*',
            '',
            "* benchmark 'foo=foo2 bar=bar1': 2 tests *",
            'Name (time in ?s) *',
            '------------------*',
            'test_a[[]foo2-bar1[]]    *',
            'test_b[[]foo2-bar1[]]    *',
            '-------------------*',
            '',
            "* benchmark 'foo=foo2 bar=bar2': 2 tests *",
            'Name (time in ?s)  *',
            '-------------------*',
            'test_a[[]foo2-bar2[]]    *',
            'test_b[[]foo2-bar2[]]    *',
            '------------------*',
            '',
            'Legend:',
            '  Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd ' 'Quartile.',
            '============* 8 passed * ============*',
        ]
    )


def test_group_by_fullname(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'fullname', test_x, test_y)
    result.stdout.fnmatch_lines_random(
        [
            "* benchmark 'test_x.py::test_a[[]0[]]': 1 tests *",
            "* benchmark 'test_x.py::test_a[[]1[]]': 1 tests *",
            "* benchmark 'test_x.py::test_b[[]0[]]': 1 tests *",
            "* benchmark 'test_x.py::test_b[[]1[]]': 1 tests *",
            "* benchmark 'test_y.py::test_a[[]0[]]': 1 tests *",
            "* benchmark 'test_y.py::test_a[[]1[]]': 1 tests *",
            "* benchmark 'test_y.py::test_b[[]0[]]': 1 tests *",
            "* benchmark 'test_y.py::test_b[[]1[]]': 1 tests *",
            '============* 8 passed * ============*',
        ]
    )


def test_double_use(testdir):
    test = testdir.makepyfile(
        """
def test_a(benchmark):
    benchmark(lambda: None)
    benchmark.pedantic(lambda: None)

def test_b(benchmark):
    benchmark.pedantic(lambda: None)
    benchmark(lambda: None)
"""
    )
    result = testdir.runpytest_subprocess(test, '--tb=line')
    result.stdout.fnmatch_lines(
        [
            '*FixtureAlreadyUsed: Fixture can only be used once. Previously it was used in benchmark(...) mode.',
            '*FixtureAlreadyUsed: Fixture can only be used once. Previously it was used in benchmark.pedantic(...) mode.',
        ]
    )


def test_only_override_skip(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-only', '--benchmark-skip', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 2 items',
            'test_only_override_skip.py ..*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_fast          *',
            'test_slow          *',
            '------*',
            '*====== 2 passed * ======*',
        ]
    )


def test_fixtures_also_skipped(testdir):
    test = testdir.makepyfile(FIXTURES_ALSO_SKIPPED_TEST)
    result = testdir.runpytest_subprocess('--benchmark-only', '-s', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 2 items',
            '*====== 1 passed, 1 skipped in * ======*',
        ]
    )
    assert 'dep created' not in result.stdout.lines


def test_conflict_between_only_and_disable(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-only', '--benchmark-disable', test)
    result.stderr.fnmatch_lines(
        [
            "ERROR: Can't have both --benchmark-only and --benchmark-disable options. Note that --benchmark-disable is "
            "automatically activated if xdist is on or you're missing the statistics dependency."
        ]
    )


def test_max_time_min_rounds(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-max-time=0.000001', '--benchmark-min-rounds=1', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 3 items',
            'test_max_time_min_rounds.py ...*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_fast          * 1  *',
            'test_slow          * 1  *',
            '------*',
            '*====== 3 passed * ======*',
        ]
    )


def test_max_time(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-max-time=0.000001', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 3 items',
            'test_max_time.py ...*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_fast          * 5  *',
            'test_slow          * 5  *',
            '------*',
            '*====== 3 passed * ======*',
        ]
    )


def test_bogus_max_time(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-max-time=bogus', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-max-time: Invalid decimal value 'bogus': InvalidOperation*",
        ]
    )


@pytest.mark.skipif("platform.python_implementation() == 'PyPy'")
def test_pep418_timer(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-timer=pep418.perf_counter', test
    )
    result.stdout.fnmatch_lines(
        [
            '* (defaults: timer=*.perf_counter*',
        ]
    )


def test_bad_save(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-save=asd:f?', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-save: Must not contain any of these characters: /:*?<>|\\ (it has ':?')",
        ]
    )


def test_bad_save_2(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-save=', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-save: Can't be empty.",
        ]
    )


def test_bad_compare_fail(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-compare-fail=?', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-compare-fail: Could not parse value: '?'.",
        ]
    )


def test_bad_rounds(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-min-rounds=asd', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-min-rounds: invalid literal for int() with base 10: 'asd'",
        ]
    )


def test_bad_rounds_2(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-min-rounds=0', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            '*: error: argument --benchmark-min-rounds: Value for --benchmark-rounds must be at least 1.',
        ]
    )


def test_compare(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0001', '--benchmark-compare-fail=min:0.1', test
    )
    result.stderr.fnmatch_lines(
        [
            'Comparing against benchmarks from: *0001_unversioned_*.json',
        ]
    )
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0001', '--benchmark-compare-fail=min:1%', test
    )
    result.stderr.fnmatch_lines(
        [
            'Comparing against benchmarks from: *0001_unversioned_*.json',
        ]
    )


def test_compare_last(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare', '--benchmark-compare-fail=min:0.1', test
    )
    result.stderr.fnmatch_lines(
        [
            'Comparing against benchmarks from: *0001_unversioned_*.json',
        ]
    )
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare', '--benchmark-compare-fail=min:1%', test
    )
    result.stderr.fnmatch_lines(
        [
            'Comparing against benchmarks from: *0001_unversioned_*.json',
        ]
    )


def test_compare_non_existing(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0002', '-rw', test)
    result.stderr.fnmatch_lines(
        [
            "* PytestBenchmarkWarning: Can't compare. No benchmark files * '0002'.",
        ]
    )


def test_compare_non_existing_verbose(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0002', test, '--benchmark-verbose'
    )
    result.stderr.fnmatch_lines(
        [
            " WARNING: Can't compare. No benchmark files * '0002'.",
        ]
    )


def test_compare_no_files(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '-rw', test, '--benchmark-compare')
    result.stderr.fnmatch_lines(["* PytestBenchmarkWarning: Can't compare. No benchmark files in '*'. Can't load the previous benchmark."])


def test_compare_no_files_verbose(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', test, '--benchmark-compare', '--benchmark-verbose'
    )
    result.stderr.fnmatch_lines([" WARNING: Can't compare. No benchmark files in '*'." " Can't load the previous benchmark."])


def test_compare_no_files_match(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '-rw', test, '--benchmark-compare=1')
    result.stderr.fnmatch_lines(["* PytestBenchmarkWarning: Can't compare. No benchmark files in '*' match '1'."])


def test_compare_no_files_match_verbose(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess(
        '--benchmark-max-time=0.0000001', '--doctest-modules', test, '--benchmark-compare=1', '--benchmark-verbose'
    )
    result.stderr.fnmatch_lines([" WARNING: Can't compare. No benchmark files in '*' match '1'."])


def test_verbose(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-verbose', '-vv', test)
    result.stderr.fnmatch_lines(
        [
            '  Calibrating to target round *s; will estimate when reaching *s (using: *, precision: *).',
            '    Measured * iterations: *s.',
            '  Running * rounds x * iterations ...',
            '  Ran for *s.',
        ]
    )


def test_save(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-save=foobar', '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines(
        [
            'Saved benchmark data in: *',
        ]
    )
    json.loads(testdir.tmpdir.join('.benchmarks').listdir()[0].join('0001_foobar.json').read())


def test_save_extra_info(testdir):
    test = testdir.makepyfile(
        """
    def test_extra(benchmark):
        benchmark.extra_info['foo'] = 'bar'
        benchmark(lambda: None)
    """
    )
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-save=foobar', '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines(
        [
            'Saved benchmark data in: *',
        ]
    )
    info = json.loads(testdir.tmpdir.join('.benchmarks').listdir()[0].join('0001_foobar.json').read())
    bench_info = info['benchmarks'][0]
    assert bench_info['name'] == 'test_extra'
    assert bench_info['extra_info'] == {'foo': 'bar'}


def test_update_machine_info_hook_detection(testdir):
    """Tests detection and execution and update_machine_info_hooks.

    Verifies that machine info hooks are detected and executed in nested
    `conftest.py`s.

    """

    record_path_conftest = """
import os

def pytest_benchmark_update_machine_info(config, machine_info):
    machine_info["conftest_path"] = (
        machine_info.get("conftest_path", []) + [os.path.relpath(__file__)]
    )
    """

    simple_test = """
def test_simple(benchmark):
    @benchmark
    def resuilt():
        1+1
    """

    testdir.makepyfile(
        **{
            'conftest': record_path_conftest,
            'test_module/conftest': record_path_conftest,
            'test_module/tests/conftest': record_path_conftest,
            'test_module/tests/simple_test.py': simple_test,
        }
    )

    def run_verify_pytest(*args):
        testdir.runpytest_subprocess('--benchmark-json=benchmark.json', '--benchmark-max-time=0.0000001', *args)

        benchmark_json = json.loads(testdir.tmpdir.join('benchmark.json').read())
        machine_info = benchmark_json['machine_info']

        assert sorted(i.replace('\\', '/') for i in machine_info['conftest_path']) == sorted(
            [
                'conftest.py',
                'test_module/conftest.py',
                'test_module/tests/conftest.py',
            ]
        )

    run_verify_pytest('test_module/tests')
    run_verify_pytest('test_module')
    run_verify_pytest('.')


def test_histogram(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-histogram=foobar', '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines(
        [
            'Generated histogram: *foobar.svg',
        ]
    )
    assert [f.basename for f in testdir.tmpdir.listdir('*.svg', sort=True)] == [
        'foobar.svg',
    ]


def test_autosave(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-autosave', '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines(
        [
            'Saved benchmark data in: *',
        ]
    )
    json.loads(testdir.tmpdir.join('.benchmarks').listdir()[0].listdir('0001_*.json')[0].read())


def test_bogus_min_time(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-min-time=bogus', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-min-time: Invalid decimal value 'bogus': InvalidOperation*",
        ]
    )


def test_disable_gc(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-disable-gc', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 2 items',
            'test_disable_gc.py ..*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_fast          *',
            'test_slow          *',
            '------*',
            '*====== 2 passed * ======*',
        ]
    )


def test_custom_timer(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-timer=time.time', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 2 items',
            'test_custom_timer.py ..*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_fast          *',
            'test_slow          *',
            '------*',
            '*====== 2 passed * ======*',
        ]
    )


def test_bogus_timer(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-timer=bogus', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            '*: error: argument --benchmark-timer: Value for --benchmark-timer must be in dotted form. Eg: ' "'module.attr'.",
        ]
    )


def test_sort_by_mean(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-sort=mean', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 2 items',
            'test_sort_by_mean.py ..*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_fast          *',
            'test_slow          *',
            '------*',
            '*====== 2 passed * ======*',
        ]
    )


def test_bogus_sort(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-sort=bogus', test)
    result.stderr.fnmatch_lines(
        [
            '*usage: *',
            "*: error: argument --benchmark-sort: Unacceptable value: 'bogus'. Value for --benchmark-sort must be one "
            "of: 'min', 'max', 'mean', 'stddev', 'name', 'fullname'.",
        ]
    )


def test_xdist(testdir):
    pytest.importorskip('xdist')
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '-n', '1', '-rw', test)
    result.stderr.fnmatch_lines(
        [
            '* Benchmarks are automatically disabled because xdist plugin is active.Benchmarks cannot be '
            'performed reliably in a parallelized environment.',
        ]
    )


def test_xdist_verbose(testdir):
    pytest.importorskip('xdist')
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '-n', '1', '--benchmark-verbose', test)
    result.stderr.fnmatch_lines(
        [
            '------*',
            ' WARNING: Benchmarks are automatically disabled because xdist plugin is active.Benchmarks cannot be performed '
            'reliably in a parallelized environment.',
            '------*',
        ]
    )


def test_cprofile(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-cprofile=cumtime', test)
    result.stdout.fnmatch_lines(
        [
            '------------*----------- cProfile (time in s) ------------*-----------',
            'test_cprofile.py::test_fast',
            'ncalls	tottime	percall	cumtime	percall	filename:lineno(function)',
            # "1	0.0000	0.0000	0.0001	0.0001	test_cprofile0/test_cprofile.py:9(result)",
            # "1	0.0001	0.0001	0.0001	0.0001	~:0(<built-in method time.sleep>)",
            # "1	0.0000	0.0000	0.0000	0.0000	~:0(<method 'disable' of '_lsprof.Profiler' objects>)",
            '',
            'test_cprofile.py::test_slow',
            'ncalls	tottime	percall	cumtime	percall	filename:lineno(function)',
            # "1	0.0000	0.0000	0.1002	0.1002	test_cprofile0/test_cprofile.py:15(<lambda>)",
            # "1	0.1002	0.1002	0.1002	0.1002	~:0(<built-in method time.sleep>)",
            # "1	0.0000	0.0000	0.0000	0.0000	~:0(<method 'disable' of '_lsprof.Profiler' objects>)",
        ]
    )


def test_disabled_and_cprofile(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--benchmark-disable', '--benchmark-cprofile=cumtime', test)
    result.stdout.fnmatch_lines(
        [
            '*==== 2 passed*',
        ]
    )


def test_abort_broken(testdir):
    """
    Test that we don't benchmark code that raises exceptions.
    """
    test = testdir.makepyfile(
        '''
"""
    >>> print('Yay, doctests!')
    Yay, doctests!
"""
import time
import pytest

def test_bad(benchmark):
    @benchmark
    def result():
        raise Exception()
    assert 1 == 1

def test_bad2(benchmark):
    @benchmark
    def result():
        time.sleep(0.1)
    assert 1 == 0

@pytest.fixture(params=['a', 'b', 'c'])
def bad_fixture(request):
    raise ImportError()

def test_ok(benchmark, bad_fixture):
    @benchmark
    def result():
        time.sleep(0.1)
    assert 1 == 0
'''
    )
    result = testdir.runpytest_subprocess('-vv', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items',
            '*',
            'test_abort_broken.py::test_bad FAILED*',
            'test_abort_broken.py::test_bad2 FAILED*',
            'test_abort_broken.py::test_ok*a* ERROR*',
            'test_abort_broken.py::test_ok*b* ERROR*',
            'test_abort_broken.py::test_ok*c* ERROR*',
            '*====== ERRORS ======*',
            '*______ ERROR at setup of test_ok[[]a[]] ______*',
            "request = <SubRequest 'bad_fixture' for <Function *test_ok*>>",
            "    @pytest.fixture(params=['a', 'b', 'c'])",
            '    def bad_fixture(request):',
            '>       raise ImportError()',
            'E       ImportError',
            'test_abort_broken.py:22: ImportError',
            '*______ ERROR at setup of test_ok[[]b[]] ______*',
            "request = <SubRequest 'bad_fixture' for <Function *test_ok*>>",
            "    @pytest.fixture(params=['a', 'b', 'c'])",
            '    def bad_fixture(request):',
            '>       raise ImportError()',
            'E       ImportError',
            'test_abort_broken.py:22: ImportError',
            '*______ ERROR at setup of test_ok[[]c[]] ______*',
            "request = <SubRequest 'bad_fixture' for <Function *test_ok*>>",
            "    @pytest.fixture(params=['a', 'b', 'c'])",
            '    def bad_fixture(request):',
            '>       raise ImportError()',
            'E       ImportError',
            'test_abort_broken.py:22: ImportError',
            '*====== FAILURES ======*',
            '*______ test_bad ______*',
            'benchmark = <pytest_benchmark.*.BenchmarkFixture object at *>',
            '    def test_bad(benchmark):',
            '?       @benchmark',
            'test_abort_broken.py:*',
            '_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _*',
            '*',
            '_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _*',
            '    @benchmark',
            '    def result():',
            '>       raise Exception()',
            'E       Exception',
            'test_abort_broken.py:11: Exception',
            '*______ test_bad2 ______*',
            'benchmark = <pytest_benchmark.*.BenchmarkFixture object at *>',
            '    def test_bad2(benchmark):',
            '        @benchmark',
            '        def result():',
            '            time.sleep(0.1)',
            '>       assert 1 == 0',
            'E       assert 1 == 0',
            'test_abort_broken.py:18: AssertionError',
        ]
    )

    result.stdout.fnmatch_lines(
        [
            '* benchmark: 1 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_bad2           *',
            '------*',
            '*====== 2 failed*, 3 error* ======*',
        ]
    )


BASIC_TEST = '''
"""
Just to make sure the plugin doesn't choke on doctests::
    >>> print('Yay, doctests!')
    Yay, doctests!
"""
import time
from functools import partial

import pytest

def test_fast(benchmark):
    @benchmark
    def result():
        return time.sleep(0.000001)
    assert result is None

def test_slow(benchmark):
    assert benchmark(partial(time.sleep, 0.001)) is None

def test_slower(benchmark):
    benchmark(lambda: time.sleep(0.01))

@pytest.mark.benchmark(min_rounds=2)
def test_xfast(benchmark):
    benchmark(str)

def test_fast(benchmark):
    benchmark(int)
'''


def test_basic(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest_subprocess('-vv', '--doctest-modules', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items',
            'test_basic.py::*test_basic PASSED*',
            'test_basic.py::test_fast PASSED*',
            'test_basic.py::test_slow PASSED*',
            'test_basic.py::test_slower PASSED*',
            'test_basic.py::test_xfast PASSED*',
            '',
            '* benchmark: 4 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_*         *',
            'test_*         *',
            'test_*         *',
            'test_*         *',
            '------*',
            '',
            '*====== 5 passed * ======*',
        ]
    )


def test_skip(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest_subprocess('-vv', '--doctest-modules', '--benchmark-skip', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items',
            'test_skip.py::*test_skip PASSED*',
            'test_skip.py::test_fast SKIPPED*',
            'test_skip.py::test_slow SKIPPED*',
            'test_skip.py::test_slower SKIPPED*',
            'test_skip.py::test_xfast SKIPPED*',
            '*====== 1 passed, 4 skipped * ======*',
        ]
    )


def test_disable(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest_subprocess('-vv', '--doctest-modules', '--benchmark-disable', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items',
            'test_disable.py::*test_disable PASSED*',
            'test_disable.py::test_fast PASSED*',
            'test_disable.py::test_slow PASSED*',
            'test_disable.py::test_slower PASSED*',
            'test_disable.py::test_xfast PASSED*',
            '*====== 5 passed * ======*',
        ]
    )


def test_mark_selection(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest_subprocess('-vv', '--doctest-modules', '-m', 'benchmark', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items*',
            'test_mark_selection.py::test_xfast PASSED*',
            '* benchmark: 1 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_xfast       *',
            '------*',
            '*====== 1 passed, 4 deselected * ======*',
        ]
    )


def test_only_benchmarks(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest_subprocess('-vv', '--doctest-modules', '--benchmark-only', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 5 items',
            'test_only_benchmarks.py::*test_only_benchmarks SKIPPED*',
            'test_only_benchmarks.py::test_fast PASSED*',
            'test_only_benchmarks.py::test_slow PASSED*',
            'test_only_benchmarks.py::test_slower PASSED*',
            'test_only_benchmarks.py::test_xfast PASSED*',
            '* benchmark: 4 tests *',
            'Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations',
            '------*',
            'test_*         *',
            'test_*         *',
            'test_*         *',
            'test_*         *',
            '------*',
            '*====== 4 passed, 1 skipped * ======*',
        ]
    )


def test_columns(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest_subprocess('--doctest-modules', '--benchmark-columns=max,iterations,min', test)
    result.stdout.fnmatch_lines(
        [
            '*collected 3 items',
            'test_columns.py ...*',
            '* benchmark: 2 tests *',
            'Name (time in ?s) * Max * Iterations * Min *',
            '------*',
        ]
    )
