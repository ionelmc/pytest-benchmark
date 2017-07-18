import argparse
import distutils.spawn
import subprocess

import pytest
from pytest import mark

from pytest_benchmark.utils import clonefunc
from pytest_benchmark.utils import get_branch_info
from pytest_benchmark.utils import get_commit_info
from pytest_benchmark.utils import get_project_name
from pytest_benchmark.utils import parse_columns
from pytest_benchmark.utils import parse_elasticsearch_storage
from pytest_benchmark.utils import parse_warmup

pytest_plugins = 'pytester',

f1 = lambda a: a


def f2(a):
    return a


@mark.parametrize('f', [f1, f2])
def test_clonefunc(f):
    assert clonefunc(f)(1) == f(1)
    assert clonefunc(f)(1) == f(1)


def test_clonefunc_not_function():
    assert clonefunc(1) == 1


@pytest.yield_fixture(params=(True, False))
def crazytestdir(request, testdir):
    if request.param:
        testdir.tmpdir.join('foo', 'bar').ensure(dir=1).chdir()

    yield testdir


@pytest.fixture(params=('git', 'hg'))
def scm(request, testdir):
    scm = request.param
    if not distutils.spawn.find_executable(scm):
        pytest.skip("%r not availabe on $PATH")
    subprocess.check_call([scm, 'init', '.'])
    if scm == 'git':
        subprocess.check_call('git config user.email you@example.com'.split())
        subprocess.check_call('git config user.name you'.split())
    else:
        testdir.tmpdir.join('.hg', 'hgrc').write("""
[ui]
username = you <you@example.com>
""")
    return scm


def test_get_commit_info(scm, crazytestdir):
    with open('test_get_commit_info.py', 'w') as fh:
        fh.write('asdf')
    subprocess.check_call([scm, 'add', 'test_get_commit_info.py'])
    subprocess.check_call([scm, 'commit', '-m', 'asdf'])
    out = get_commit_info()
    branch = 'master' if scm == 'git' else 'default'
    assert out['branch'] == branch

    assert out.get('dirty') == False
    assert 'id' in out

    with open('test_get_commit_info.py', 'w') as fh:
        fh.write('sadf')
    out = get_commit_info()

    assert out.get('dirty') == True
    assert 'id' in out


def test_get_branch_info(scm, testdir):
    # make an initial commit
    testdir.tmpdir.join('foo.txt').ensure(file=True)
    subprocess.check_call([scm, 'add', 'foo.txt'])
    subprocess.check_call([scm, 'commit', '-m', 'added foo.txt'])
    branch = get_branch_info()
    expected = 'master' if scm == 'git' else 'default'
    assert branch == expected
    #
    # switch to a branch
    if scm == 'git':
        subprocess.check_call(['git', 'checkout', '-b', 'mybranch'])
    else:
        subprocess.check_call(['hg', 'branch', 'mybranch'])
    branch = get_branch_info()
    assert branch == 'mybranch'
    #
    # git only: test detached head
    if scm == 'git':
        subprocess.check_call(['git', 'commit', '--allow-empty', '-m', '...'])
        subprocess.check_call(['git', 'commit', '--allow-empty', '-m', '...'])
        subprocess.check_call(['git', 'checkout', 'HEAD~1'])
        assert get_branch_info() == '(detached head)'


def test_no_branch_info(testdir):
    assert get_branch_info() == '(unknown vcs)'


def test_branch_info_error(testdir):
    testdir.mkdir('.git')
    assert get_branch_info() == '(error: fatal: Not a git repository (or any of the parent directories): .git)'


def test_parse_warmup():
    assert parse_warmup('yes') == True
    assert parse_warmup('on') == True
    assert parse_warmup('true') == True
    assert parse_warmup('off') == False
    assert parse_warmup('off') == False
    assert parse_warmup('no') == False
    assert parse_warmup('') == True
    assert parse_warmup('auto') in [True, False]


def test_parse_columns():
    assert parse_columns('min,max') == ['min', 'max']
    assert parse_columns('MIN, max  ') == ['min', 'max']
    with pytest.raises(argparse.ArgumentTypeError):
        parse_columns('min,max,x')


@mark.parametrize('scm', [None, 'git', 'hg'])
@mark.parametrize('set_remote', [
    False,
    'https://example.com/pytest_benchmark_repo',
    'https://example.com/pytest_benchmark_repo.git',
    'c:\\foo\\bar\\pytest_benchmark_repo.git'
    'foo@example.com:pytest_benchmark_repo.git'])
def test_get_project_name(scm, set_remote, testdir):
    if scm is None:
        assert get_project_name().startswith("test_get_project_name")
        return
    if not distutils.spawn.find_executable(scm):
        pytest.skip("%r not availabe on $PATH")
    subprocess.check_call([scm, 'init', '.'])
    if scm == 'git' and set_remote:
        subprocess.check_call(['git', 'config', 'remote.origin.url', set_remote])
    elif scm == 'hg' and set_remote:
        set_remote = set_remote.replace('.git', '')
        set_remote = set_remote.replace('.com:', '/')
        testdir.tmpdir.join('.hg', 'hgrc').write(
            "[ui]\n"
            "username = you <you@example.com>\n"
            "[paths]\n"
            "default = %s\n" % set_remote)
    if set_remote:
        assert get_project_name() == "pytest_benchmark_repo"
    else:
        # use directory name if remote branch is not set
        assert get_project_name().startswith("test_get_project_name")


def test_parse_elasticsearch_storage():
    assert parse_elasticsearch_storage("http://localhost:9200") == (
    ["http://localhost:9200"], "benchmark", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://localhost:9200/benchmark2") == (
    ["http://localhost:9200"], "benchmark2", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://localhost:9200/benchmark2/benchmark2") == (
    ["http://localhost:9200"], "benchmark2", "benchmark2", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://host1:9200,host2:9200") == (
    ["http://host1:9200", "http://host2:9200"], "benchmark", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://host1:9200,host2:9200/benchmark2") == (
    ["http://host1:9200", "http://host2:9200"], "benchmark2", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://localhost:9200/benchmark2/benchmark2?project_name=project_name") == (
    ["http://localhost:9200"], "benchmark2", "benchmark2", "project_name")
