import py
import pytest

pytest_plugins = 'pytester',

THIS = py.path.local(__file__)
STORAGE = THIS.dirpath('test_storage')


@pytest.mark.parametrize('arg', ['--help', 'help'])
def test_help(testdir, arg):
    result = testdir.run('py.test-benchmark', arg)
    result.stdout.fnmatch_lines([
        "usage: py.test-benchmark [-h [COMMAND]] [--storage URI] [--verbose]",
        "                         {help,list,compare} ...",
        "",
        "pytest_benchmark's management commands.",
        "",
        "optional arguments:",
        "  -h [COMMAND], --help [COMMAND]",
        "                        Display help and exit.",
        "  --storage URI, -s URI",
        "                        Specify a path to store the runs as uri in form",
        "                        file://path or elasticsearch+http[s]://host1,host2/[in",
        "                        dex/doctype?project_name=Project] (when --benchmark-",
        "                        save or --benchmark-autosave are used). For backwards",
        "                        compatibility unexpected values are converted to",
        "                        file://<value>. Default: 'file://./.benchmarks'.",
        "  --verbose, -v         Dump diagnostic and progress information.",
        "",
        "commands:",
        "  {help,list,compare}",
        "    help                Display help and exit.",
        "    list                List saved runs.",
        "    compare             Compare saved runs.",
    ])
    assert result.ret == 0


@pytest.mark.parametrize('args', ['list --help', 'help list'])
def test_help_list(testdir, args):
    result = testdir.run('py.test-benchmark', *args.split())
    result.stdout.fnmatch_lines([
        "usage: py.test-benchmark list [-h]",
        "",
        "List saved runs.",
        "",
        "optional arguments:",
        "  -h, --help  show this help message and exit",
    ])
    assert result.ret == 0


@pytest.mark.parametrize('args', ['compare --help', 'help compare'])
def test_help_compare(testdir, args):
    result = testdir.run('py.test-benchmark', *args.split())
    result.stdout.fnmatch_lines([
        "usage: py.test-benchmark compare [-h] [--sort COL] [--group-by LABEL]",
        "                                 [--columns LABELS] [--name FORMAT]",
        "                                 [--histogram [FILENAME-PREFIX]]",
        "                                 [--csv [FILENAME]]",
        "                                 [glob_or_file [glob_or_file ...]]",
        "",
        "Compare saved runs.",
        "",
        "positional arguments:",
        "  glob_or_file          Glob or exact path for json files. If not specified",
        "                        all runs are loaded.",
        "",
        "optional arguments:",
        "  -h, --help            show this help message and exit",
        "  --sort COL            Column to sort on. Can be one of: 'min', 'max',",
        "                        'mean', 'stddev', 'name', 'fullname'. Default: 'min'",
        "  --group-by LABEL      How to group tests. Can be one of: 'group', 'name',",
        "                        'fullname', 'func', 'fullfunc', 'param' or",
        "                        'param:NAME', where NAME is the name passed to",
        "                        @pytest.parametrize. Default: 'group'",
        "  --columns LABELS      Comma-separated list of columns to show in the result",
        "                        table. Default: 'min, max, mean, stddev, median, iqr,",
        "                        outliers, rounds, iterations'",
        "  --name FORMAT         How to format names in results. Can be one of 'short',",
        "                        'normal', 'long'. Default: 'normal'",
        "  --histogram [FILENAME-PREFIX]",
        "                        Plot graphs of min/max/avg/stddev over time in",
        "                        FILENAME-PREFIX-test_name.svg. If FILENAME-PREFIX",
        "                        contains slashes ('/') then directories will be",
        "                        created. Default: 'benchmark_*'",
        "  --csv [FILENAME]      Save a csv report. If FILENAME contains slashes ('/')",
        "                        then directories will be created. Default:",
        "                        'benchmark_*'",
        "",
        "examples:",
        "",
        "    pytest-benchmark compare 'Linux-CPython-3.5-64bit/*'",
        "",
        "        Loads all benchmarks ran with that interpreter. Note the special quoting that disables your shell's "
        "glob",
        "        expansion.",
        "",
        "    pytest-benchmark compare 0001",
        "",
        "        Loads first run from all the interpreters.",
        "",
        "    pytest-benchmark compare /foo/bar/0001_abc.json /lorem/ipsum/0001_sir_dolor.json",
        "",
        "        Loads runs from exactly those files.",
    ])
    assert result.ret == 0


def test_list(testdir):
    result = testdir.run('py.test-benchmark', '--storage', STORAGE, 'list')
    assert result.stderr.lines == []
    result.stdout.fnmatch_lines([
        '*0001_*.json',
        '*0002_*.json',
        '*0003_*.json',
        '*0004_*.json',
        '*0005_*.json',
        '*0006_*.json',
        '*0007_*.json',
        '*0008_*.json',
        '*0009_*.json',
        '*0010_*.json',
        '*0011_*.json',
        '*0012_*.json',
        '*0013_*.json',
        '*0014_*.json',
        '*0015_*.json',
        '*0016_*.json',
        '*0017_*.json',
        '*0018_*.json',
        '*0019_*.json',
        '*0020_*.json',
        '*0021_*.json',
        '*0022_*.json',
        '*0023_*.json',
        '*0024_*.json',
        '*0025_*.json',
        '*0026_*.json',
        '*0027_*.json',
        '*0028_*.json',
        '*0029_*.json',
        '*0030_*.json',
    ])
    assert result.ret == 0
