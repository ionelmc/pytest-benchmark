import json
import platform

import pytest

pytest_plugins = 'pytester',
platform


def test_help(testdir):
    result = testdir.runpytest('--help')
    result.stdout.fnmatch_lines([
        "*", "*",
        "benchmark:",
        "  --benchmark-min-time=SECONDS",
        "                        Minimum time per round in seconds. Default: '0.000005'",
        "  --benchmark-max-time=SECONDS",
        "                        Maximum time to spend in a benchmark in seconds.",
        "                        Default: '1.0'",
        "  --benchmark-min-rounds=NUM",
        "                        Minimum rounds, even if total time would exceed",
        "                        `--max-time`. Default: 5",
        "  --benchmark-sort=COL  Column to sort on. Can be one of: 'min', 'max', 'mean'",
        "                        or 'stddev'. Default: 'min'",
        "  --benchmark-group-by=LABEL",
        "                        How to group tests. Can be one of: 'group', 'name',",
        "                        'fullname', 'func', 'fullfunc' or 'param'. Default:",
        "                        'group'",
        "  --benchmark-timer=FUNC",
        "                        Timer to use when measuring time. Default:*",
        "  --benchmark-calibration-precision=NUM",
        "                        Precision to use when calibrating number of",
        "                        iterations. Precision of 10 will make the timer look",
        "                        10 times more accurate, at a cost of less precise",
        "                        measure of deviations. Default: 10",
        "  --benchmark-warmup    Activates warmup. Will run the test function up to",
        "                        number of times in the calibration phase. See",
        "                        `--benchmark-warmup-iterations`. Note: Even the warmup",
        "                        phase obeys --benchmark-max-time.",
        "  --benchmark-warmup-iterations=NUM",
        "                        Max number of iterations to run in the warmup phase.",
        "                        Default: 100000",
        "  --benchmark-verbose   Dump diagnostic and progress information.",
        "  --benchmark-disable-gc",
        "                        Disable GC during benchmarks.",
        "  --benchmark-skip      Skip running any benchmarks.",
        "  --benchmark-only      Only run benchmarks.",
        "  --benchmark-save=NAME",
        "                        Save the current run into 'STORAGE-PATH/counter-",
        "                        NAME.json'.",
        "  --benchmark-autosave  Autosave the current run into 'STORAGE-PATH/counter-",
        "                        *.json",
        "  --benchmark-save-data",
        "                        Use this to make --benchmark-save and --benchmark-",
        "                        autosave include all the timing data, not just the",
        "                        stats.",
        "  --benchmark-compare=[NUM]",
        "                        Compare the current run against run NUM or the latest",
        "                        saved run if unspecified.",
        "  --benchmark-compare-fail=EXPR=[EXPR=...]",
        "                        Fail test if performance regresses according to given",
        "                        EXPR (eg: min:5% or mean:0.001 for number of seconds).",
        "                        Can be used multiple times.",
        "  --benchmark-storage=STORAGE-PATH",
        "                        Specify a different path to store the runs (when",
        "                        --benchmark-save or --benchmark-autosave are used).",
        "                        Default: './.benchmarks/*'",
        "  --benchmark-histogram=[FILENAME-PREFIX]",
        "                        Plot graphs of min/max/avg/stddev over time in",
        "                        FILENAME-PREFIX-test_name.svg. Default:",
        "                        'benchmark_*'",
        "  --benchmark-json=PATH",
        "                        Dump a JSON report into PATH. Note that this will",
        "                        include the complete data (all the timings, not just",
        "                        the stats).",
        "*",
    ])


def test_groups(testdir):
    test = testdir.makepyfile('''"""
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
''')
    result = testdir.runpytest('-vv', '--doctest-modules', test)
    result.stdout.fnmatch_lines([
        "*collected 5 items",
        "*",
        "test_groups.py::*test_groups PASSED",
        "test_groups.py::test_fast PASSED",
        "test_groups.py::test_slow PASSED",
        "test_groups.py::test_slower PASSED",
        "test_groups.py::test_xfast PASSED",
        "*",
        "* benchmark: 2 tests *",
        "*",
        "* benchmark 'A': 2 tests *",
        "*",
        "*====== 5 passed* seconds ======*",
    ])


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

GROUPING_TEST = '''
import pytest

@pytest.mark.parametrize("foo", range(2))
@pytest.mark.benchmark(group="A")
def test_a(benchmark, foo):
    benchmark(str)

@pytest.mark.parametrize("foo", range(2))
@pytest.mark.benchmark(group="B")
def test_b(benchmark, foo):
    benchmark(int)
'''


def test_group_by_name(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'name', test_x, test_y)
    result.stdout.fnmatch_lines([
        '*', '*', '*', '*', '*',
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
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
    ])


def test_group_by_func(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'func', test_x, test_y)
    result.stdout.fnmatch_lines([
        '*', '*', '*', '*', '*',
        "* benchmark 'test_a': 4 tests *",
        'Name (time in ?s)     *',
        '----------------------*',
        'test_a[[]0[]]             *',
        'test_a[[]1[]]             *',
        'test_a[[]0[]]             *',
        'test_a[[]1[]]             *',
        '----------------------*',
        '*', '*',
        "* benchmark 'test_b': 4 tests *",
        'Name (time in ?s)     *',
        '----------------------*',
        'test_b[[]0[]]             *',
        'test_b[[]1[]]             *',
        'test_b[[]0[]]             *',
        'test_b[[]1[]]             *',
        '----------------------*',
        '*', '*',
        '============* 8 passed* seconds ============*',
    ])


def test_group_by_fullfunc(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'fullfunc', test_x, test_y)
    result.stdout.fnmatch_lines([
        '*', '*', '*', '*', '*',
        "* benchmark 'test_x.py::test_a': 2 tests *",
        'Name (time in ?s) *',
        '------------------*',
        'test_a[[]0[]]         *',
        'test_a[[]1[]]         *',
        '------------------*',
        '(*) Outliers: 1 Standard Deviation from M*',
        '*',
        "* benchmark 'test_x.py::test_b': 2 tests *",
        'Name (time in ?s) *',
        '------------------*',
        'test_b[[]0[]]         *',
        'test_b[[]1[]]         *',
        '------------------*',
        '(*) Outliers: 1 Standard Deviation from M*',
        '*',
        "* benchmark 'test_y.py::test_a': 2 tests *",
        'Name (time in ?s) *',
        '------------------*',
        'test_a[[]0[]]         *',
        'test_a[[]1[]]         *',
        '------------------*',
        '(*) Outliers: 1 Standard Deviation from M*',
        '*',
        "* benchmark 'test_y.py::test_b': 2 tests *",
        'Name (time in ?s) *',
        '------------------*',
        'test_b[[]0[]]         *',
        'test_b[[]1[]]         *',
        '------------------*',
        '(*) Outliers: 1 Standard Deviation from M*',
        '*',
        '============* 8 passed* seconds ============*',
    ])


def test_group_by_param(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'param', test_x, test_y)
    result.stdout.fnmatch_lines([
        '*', '*', '*', '*', '*',
        "* benchmark '0': 4 tests *",
        'Name (time in ?s)  *',
        '-------------------*',
        'test_a[[]0[]]          *',
        'test_b[[]0[]]          *',
        'test_a[[]0[]]          *',
        'test_b[[]0[]]          *',
        '-------------------*',
        '(*) Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd '
        'Quartile.',
        '',
        "* benchmark '1': 4 tests *",
        'Name (time in ?s) *',
        '------------------*',
        'test_a[[]1[]]         *',
        'test_b[[]1[]]         *',
        'test_a[[]1[]]         *',
        'test_b[[]1[]]         *',
        '------------------*',
        '(*) Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd '
        'Quartile.',
        '',
        '============* 8 passed* seconds ============*',
    ])


def test_group_by_fullname(testdir):
    test_x = testdir.makepyfile(test_x=GROUPING_TEST)
    test_y = testdir.makepyfile(test_y=GROUPING_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--benchmark-group-by', 'fullname', test_x, test_y)
    result.stdout.fnmatch_lines_random([
        "* benchmark 'test_x.py::test_a[[]0[]]': 1 tests *",
        "* benchmark 'test_x.py::test_a[[]1[]]': 1 tests *",
        "* benchmark 'test_x.py::test_b[[]0[]]': 1 tests *",
        "* benchmark 'test_x.py::test_b[[]1[]]': 1 tests *",
        "* benchmark 'test_y.py::test_a[[]0[]]': 1 tests *",
        "* benchmark 'test_y.py::test_a[[]1[]]': 1 tests *",
        "* benchmark 'test_y.py::test_b[[]0[]]': 1 tests *",
        "* benchmark 'test_y.py::test_b[[]1[]]': 1 tests *",
        '============* 8 passed* seconds ============*',
    ])


def test_conflict_between_only_and_skip(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-only', '--benchmark-skip', test)
    result.stderr.fnmatch_lines([
        "ERROR: Can't have both --benchmark-only and --benchmark-skip options."
    ])


def test_max_time_min_rounds(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-max-time=0.000001', '--benchmark-min-rounds=1', test)
    result.stdout.fnmatch_lines([
        "*collected 3 items",
        "test_max_time_min_rounds.py ...",
        "Benchmark global settings:",
        "    minimum number of rounds: 1",
        "    minimum time per rounds: 5.00us",
        "    maximum total time per test: 1.00us",
        "    timer: *",
        "* benchmark: 2 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_fast          * 1  *",
        "test_slow          * 1  *",
        "------*",
        "*====== 3 passed* seconds ======*",
    ])


def test_max_time(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-max-time=0.000001', test)
    result.stdout.fnmatch_lines([
        "*collected 3 items",
        "test_max_time.py ...",
        "Benchmark global settings:",
        "    minimum number of rounds: 5",
        "    minimum time per rounds: 5.00us",
        "    maximum total time per test: 1.00us",
        "    timer: *",
        "* benchmark: 2 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_fast          * 5  *",
        "test_slow          * 5  *",
        "------*",
        "*====== 3 passed* seconds ======*",
    ])


def test_bogus_max_time(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-max-time=bogus', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-max-time: Invalid decimal value 'bogus': InvalidOperation*",
    ])


@pytest.mark.skipif("platform.python_implementation() == 'PyPy'")
def test_pep418_timer(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules',
                               '--benchmark-timer=pep418.perf_counter', test)
    result.stdout.fnmatch_lines([
        "    timer: *.perf_counter",
    ])


def test_bad_save(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-save=asd:f?', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-save: Must not contain any of these characters: /:*?<>|\\ (it has ':?')",
    ])


def test_bad_save_2(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-save=', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-save: Can't be empty.",
    ])


def test_bad_compare_fail(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-compare-fail=?', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-compare-fail: Could not parse value.",
    ])


def test_bad_rounds(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-min-rounds=asd', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-min-rounds: invalid literal for int() with base 10: 'asd'",
    ])


def test_bad_rounds_2(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-min-rounds=0', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-min-rounds: Value for --benchmark-rounds must be at least 1.",
    ])


def test_compare(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0001',
                               '--benchmark-compare-fail=min:0.1', test)
    result.stderr.fnmatch_lines([
        "Comparing against benchmark 0001_unversioned_*.json:",
    ])
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0001',
                               '--benchmark-compare-fail=min:1%', test)
    result.stderr.fnmatch_lines([
        "Comparing against benchmark 0001_unversioned_*.json:",
    ])


def test_compare_last(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare',
                               '--benchmark-compare-fail=min:0.1', test)
    result.stderr.fnmatch_lines([
        "Comparing against benchmark 0001_unversioned_*.json:",
    ])
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare',
                               '--benchmark-compare-fail=min:1%', test)
    result.stderr.fnmatch_lines([
        "Comparing against benchmark 0001_unversioned_*.json:",
    ])


def test_compare_non_existing(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0002',
                               test)
    result.stderr.fnmatch_lines([
        " WARNING: Can't compare. No benchmark files matched '0002'",
    ])


def test_compare_no_files(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', test, '--benchmark-compare')
    result.stderr.fnmatch_lines([
         " WARNING: Can't compare. No benchmark files in '*'. Expected files matching *.json."
         " Can't load the previous benchmark."
    ])


def test_compare_no_files_match(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', test, '--benchmark-compare=1')
    result.stderr.fnmatch_lines([
         " WARNING: Can't compare. No benchmark files in '*'. Expected files matching *.json."
         " Can't match anything to '1'."
    ])


def test_compare_too_many(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-autosave', test)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-compare=0',
                               test)
    result.stderr.fnmatch_lines([
        " WARNING: Can't compare. Too many benchmark files matched '0':",
        ' - *0001_unversioned_*.json',
        ' - *0002_unversioned_*.json',
    ])


def test_verbose(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-max-time=0.0000001', '--doctest-modules', '--benchmark-verbose',
                               '-vv', test)
    result.stderr.fnmatch_lines([
        "  Timer precision: *s",
        "  Calibrating to target round *s; will estimate when reaching *s.",
        "    Measured * iterations: *s.",
        "  Running * rounds x * iterations ...",
        "  Ran for *s.",
    ])


def test_save(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-save=foobar',
                               '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines([
        "Saved benchmark data in *",
    ])
    json.loads(testdir.tmpdir.join('.benchmarks').listdir()[0].join('0001_foobar.json').read())


def test_histogram(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-histogram=foobar',
                               '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines([
        "Generated histogram *foobar-test_histogram.py_test_fast.svg",
        "Generated histogram *foobar-test_histogram.py_test_slow.svg",
    ])
    assert [f.basename for f in testdir.tmpdir.listdir("*.svg", sort=True)] == [
        'foobar-test_histogram.py_test_fast.svg',
        'foobar-test_histogram.py_test_slow.svg',
    ]


def test_autosave(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-autosave',
                               '--benchmark-max-time=0.0000001', test)
    result.stderr.fnmatch_lines([
        "Saved benchmark data in *",
    ])
    json.loads(testdir.tmpdir.join('.benchmarks').listdir()[0].listdir('0001_*.json')[0].read())


def test_bogus_min_time(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '--benchmark-min-time=bogus', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-min-time: Invalid decimal value 'bogus': InvalidOperation*",
    ])


def test_disable_gc(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-disable-gc', test)
    result.stdout.fnmatch_lines([
        "*collected 2 items",
        "test_disable_gc.py ..",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 2 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_fast          *",
        "test_slow          *",
        "------*",
        "*====== 2 passed* seconds ======*",
    ])


def test_custom_timer(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-timer=time.time', test)
    result.stdout.fnmatch_lines([
        "*collected 2 items",
        "test_custom_timer.py ..",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 2 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_fast          *",
        "test_slow          *",
        "------*",
        "*====== 2 passed* seconds ======*",
    ])


def test_bogus_timer(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-timer=bogus', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-timer: Value for --benchmark-timer must be in dotted form. Eg: "
        "'module.attr'.",
    ])


def test_sort_by_mean(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-sort=mean', test)
    result.stdout.fnmatch_lines([
        "*collected 2 items",
        "test_sort_by_mean.py ..",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 2 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_fast          *",
        "test_slow          *",
        "------*",
        "*====== 2 passed* seconds ======*",
    ])


def test_bogus_sort(testdir):
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--benchmark-sort=bogus', test)
    result.stderr.fnmatch_lines([
        "usage: py* [[]options[]] [[]file_or_dir[]] [[]file_or_dir[]] [[]...[]]",
        "py*: error: argument --benchmark-sort: Value for --benchmark-sort must be one of: 'min', 'max', "
        "'mean' or 'stddev'.",
    ])


def test_xdist(testdir):
    pytest.importorskip('xdist')
    test = testdir.makepyfile(SIMPLE_TEST)
    result = testdir.runpytest('--doctest-modules', '-n', '1', test)
    result.stderr.fnmatch_lines([
        "------*",
        " WARNING: Benchmarks are automatically skipped because xdist plugin is active.Benchmarks cannot be performed "
        "reliably in a parallelized environment.",
        "------*",
    ])


def test_abort_broken(testdir):
    """
    Test that we don't benchmark code that raises exceptions.
    """
    test = testdir.makepyfile('''
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
''')
    result = testdir.runpytest('-vv', test)
    result.stdout.fnmatch_lines([
        "*collected 5 items",

        "test_abort_broken.py::test_bad FAILED",
        "test_abort_broken.py::test_bad2 FAILED",
        "test_abort_broken.py::test_ok[a] ERROR",
        "test_abort_broken.py::test_ok[b] ERROR",
        "test_abort_broken.py::test_ok[c] ERROR",

        "*====== ERRORS ======*",
        "*______ ERROR at setup of test_ok[[]a[]] ______*",

        "request = <SubRequest 'bad_fixture' for <Function 'test_ok[a]'>>",

        "    @pytest.fixture(params=['a', 'b', 'c'])",
        "    def bad_fixture(request):",
        ">       raise ImportError()",
        "E       ImportError",

        "test_abort_broken.py:22: ImportError",
        "*______ ERROR at setup of test_ok[[]b[]] ______*",

        "request = <SubRequest 'bad_fixture' for <Function 'test_ok[b]'>>",

        "    @pytest.fixture(params=['a', 'b', 'c'])",
        "    def bad_fixture(request):",
        ">       raise ImportError()",
        "E       ImportError",

        "test_abort_broken.py:22: ImportError",
        "*______ ERROR at setup of test_ok[[]c[]] ______*",

        "request = <SubRequest 'bad_fixture' for <Function 'test_ok[c]'>>",

        "    @pytest.fixture(params=['a', 'b', 'c'])",
        "    def bad_fixture(request):",
        ">       raise ImportError()",
        "E       ImportError",

        "test_abort_broken.py:22: ImportError",
        "*====== FAILURES ======*",
        "*______ test_bad ______*",

        "benchmark = <pytest_benchmark.plugin.BenchmarkFixture object at *>",

        "    def test_bad(benchmark):",
        ">       @benchmark",
        "        def result():",

        "test_abort_broken.py:*",
        "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _*",
        "*pytest_benchmark/plugin.py:*: in __call__",
        "    duration, iterations, loops_range = self._calibrate_timer(runner)",
        "*pytest_benchmark/plugin.py:*: in _calibrate_timer",
        "    duration = runner(loops_range)",
        "*pytest_benchmark/plugin.py:*: in runner",
        "    *",
        "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _*",

        "    @benchmark",
        "    def result():",
        ">       raise Exception()",
        "E       Exception",

        "test_abort_broken.py:11: Exception",
        "*______ test_bad2 ______*",

        "benchmark = <pytest_benchmark.plugin.BenchmarkFixture object at *>",

        "    def test_bad2(benchmark):",
        "        @benchmark",
        "        def result():",
        "            time.sleep(0.1)",
        ">       assert 1 == 0",
        "E       assert 1 == 0",

        "test_abort_broken.py:18: AssertionError",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 1 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_bad2           *",
        "------*",

        "*====== 2 failed*, 3 error* seconds ======*",
    ])


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
    result = testdir.runpytest('-vv', '--doctest-modules', test)
    result.stdout.fnmatch_lines([
        "*collected 5 items",
        "test_basic.py::*test_basic PASSED",
        "test_basic.py::test_slow PASSED",
        "test_basic.py::test_slower PASSED",
        "test_basic.py::test_xfast PASSED",
        "test_basic.py::test_fast PASSED",
        "",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 4 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_slow           *",
        "test_slower         *",
        "test_xfast          *",
        "test_fast           *",
        "------*",
        "",
        "*====== 5 passed* seconds ======*",
    ])


def test_skip(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest('-vv', '--doctest-modules', '--benchmark-skip', test)
    result.stdout.fnmatch_lines([
        "*collected 5 items",
        "test_skip.py::*test_skip PASSED",
        "test_skip.py::test_slow SKIPPED",
        "test_skip.py::test_slower SKIPPED",
        "test_skip.py::test_xfast SKIPPED",
        "test_skip.py::test_fast SKIPPED",
        "*====== 1 passed, 4 skipped* seconds ======*",
    ])


def test_mark_selection(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest('-vv', '--doctest-modules', '-m', 'benchmark', test)
    result.stdout.fnmatch_lines([
        "*collected 5 items",
        "test_mark_selection.py::test_xfast PASSED",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 1 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_xfast       *",
        "------*",
        "*====== 4 tests deselected by \"-m 'benchmark'\" ======*",
        "*====== 1 passed, 4 deselected* seconds ======*",
    ])


def test_only_benchmarks(testdir):
    test = testdir.makepyfile(BASIC_TEST)
    result = testdir.runpytest('-vv', '--doctest-modules', '--benchmark-only', test)
    result.stdout.fnmatch_lines([
        "*collected 5 items",
        "test_only_benchmarks.py::*test_only_benchmarks SKIPPED",
        "test_only_benchmarks.py::test_slow PASSED",
        "test_only_benchmarks.py::test_slower PASSED",
        "test_only_benchmarks.py::test_xfast PASSED",
        "test_only_benchmarks.py::test_fast PASSED",
        "Benchmark global settings:",
        "    minimum number of rounds: *",
        "    minimum time per rounds: *",
        "    maximum total time per test: *",
        "    timer: *",
        "* benchmark: 4 tests *",
        "Name (time in ?s) * Min * Max * Mean * StdDev * Rounds * Iterations",
        "------*",
        "test_slow        *",
        "test_slower      *",
        "test_xfast       *",
        "test_fast        *",
        "------*",
        "*====== 4 passed, 1 skipped* seconds ======*",
    ])
