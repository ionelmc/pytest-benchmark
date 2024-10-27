import argparse
import os
import shutil
import subprocess

import pytest
from pytest import mark

from pytest_benchmark.utils import clonefunc
from pytest_benchmark.utils import get_commit_info
from pytest_benchmark.utils import get_project_name
from pytest_benchmark.utils import parse_columns
from pytest_benchmark.utils import parse_elasticsearch_storage
from pytest_benchmark.utils import parse_warmup

pytest_plugins = ('pytester',)

f1 = lambda a: a  # noqa


def f2(a):
    return a


@mark.parametrize('f', [f1, f2])
def test_clonefunc(f):
    assert clonefunc(f)(1) == f(1)
    assert clonefunc(f)(1) == f(1)


def test_clonefunc_not_function():
    assert clonefunc(1) == 1


@pytest.fixture(params=(True, False))
def crazytestdir(request, testdir):
    if request.param:
        testdir.tmpdir.join('foo', 'bar').ensure(dir=1).chdir()

    return testdir


@pytest.fixture(params=('git', 'hg'))
def scm(request, testdir):
    scm = request.param
    if not shutil.which(scm):
        pytest.skip(f'{scm!r} not available on $PATH')
    subprocess.check_call([scm, 'init', '.'])
    if scm == 'git':
        subprocess.check_call('git config user.email you@example.com'.split())
        subprocess.check_call('git config user.name you'.split())
    else:
        testdir.tmpdir.join('.hg', 'hgrc').write(
            """
[ui]
username = you <you@example.com>
"""
        )
    return scm


def test_get_commit_info(scm, crazytestdir):
    with open('test_get_commit_info.py', 'w') as fh:
        fh.write('asdf')
    subprocess.check_call([scm, 'add', 'test_get_commit_info.py'])
    subprocess.check_call([scm, 'commit', '-m', 'asdf'])
    out = get_commit_info()
    branch = 'master' if scm == 'git' else 'default'
    assert out['branch'] == branch

    assert out.get('dirty') is False
    assert 'id' in out

    with open('test_get_commit_info.py', 'w') as fh:
        fh.write('sadf')
    out = get_commit_info()

    assert out.get('dirty') is True
    assert 'id' in out


def test_missing_scm_bins(scm, crazytestdir, monkeypatch):
    with open('test_get_commit_info.py', 'w') as fh:
        fh.write('asdf')
    subprocess.check_call([scm, 'add', 'test_get_commit_info.py'])
    subprocess.check_call([scm, 'commit', '-m', 'asdf'])
    monkeypatch.setenv('PATH', os.getcwd())
    out = get_commit_info()
    assert (
        'No such file or directory' in out['error']
        or 'The system cannot find the file specified' in out['error']
        or 'FileNotFoundError' in out['error']
    )


def test_get_branch_info(scm, testdir):
    # make an initial commit
    testdir.tmpdir.join('foo.txt').ensure(file=True)
    subprocess.check_call([scm, 'add', 'foo.txt'])
    subprocess.check_call([scm, 'commit', '-m', 'added foo.txt'])
    branch = get_commit_info()['branch']
    expected = 'master' if scm == 'git' else 'default'
    assert branch == expected
    #
    # switch to a branch
    if scm == 'git':
        subprocess.check_call(['git', 'checkout', '-b', 'mybranch'])
    else:
        subprocess.check_call(['hg', 'branch', 'mybranch'])
    branch = get_commit_info()['branch']
    assert branch == 'mybranch'
    #
    # git only: test detached head
    if scm == 'git':
        subprocess.check_call(['git', 'commit', '--allow-empty', '-m', '...'])
        subprocess.check_call(['git', 'commit', '--allow-empty', '-m', '...'])
        subprocess.check_call(['git', 'checkout', 'HEAD~1'])
        assert get_commit_info()['branch'] == '(detached head)'


def test_no_branch_info(testdir):
    assert get_commit_info()['branch'] == '(unknown)'


def test_commit_info_error(testdir):
    testdir.mkdir('.git')
    info = get_commit_info()
    assert info['branch'].lower() == '(unknown)'.lower()
    assert info['error'].lower().startswith("calledprocesserror(128, 'fatal: not a git repository")


def test_parse_warmup():
    assert parse_warmup('yes') is True
    assert parse_warmup('on') is True
    assert parse_warmup('true') is True
    assert parse_warmup('off') is False
    assert parse_warmup('off') is False
    assert parse_warmup('no') is False
    assert parse_warmup('') is True
    assert parse_warmup('auto') in [True, False]


def test_parse_columns():
    assert parse_columns('min,max') == ['min', 'max']
    assert parse_columns('MIN, max  ') == ['min', 'max']
    with pytest.raises(argparse.ArgumentTypeError):
        parse_columns('min,max,x')


@mark.parametrize('scm', [None, 'git', 'hg'])
@mark.parametrize(
    'set_remote',
    [
        False,
        'https://example.com/pytest_benchmark_repo',
        'https://example.com/pytest_benchmark_repo.git',
        'c:\\foo\\bar\\pytest_benchmark_repo.git' 'foo@example.com:pytest_benchmark_repo.git',
    ],
)
def test_get_project_name(scm, set_remote, testdir):
    if scm is None:
        assert get_project_name().startswith('test_get_project_name')
        return
    if not shutil.which(scm):
        pytest.skip(f'{scm!r} not available on $PATH')
    subprocess.check_call([scm, 'init', '.'])
    if scm == 'git' and set_remote:
        subprocess.check_call(['git', 'config', 'remote.origin.url', set_remote])
    elif scm == 'hg' and set_remote:
        set_remote = set_remote.replace('.git', '')
        set_remote = set_remote.replace('.com:', '/')
        testdir.tmpdir.join('.hg', 'hgrc').write(f"""
[ui]
username = you <you@example.com>
[paths]
default = {set_remote}
""")
    if set_remote:
        assert get_project_name() == 'pytest_benchmark_repo'
    else:
        # use directory name if remote branch is not set
        assert get_project_name().startswith('test_get_project_name')


@mark.parametrize('scm', ['git', 'hg'])
def test_get_project_name_broken(scm, testdir):
    testdir.tmpdir.join('.' + scm).ensure(dir=1)
    assert get_project_name() in ['test_get_project_name_broken0', 'test_get_project_name_broken1']


def test_get_project_name_fallback(testdir, capfd):
    testdir.tmpdir.ensure('.hg', dir=1)
    project_name = get_project_name()
    assert project_name.startswith('test_get_project_name_fallback')
    assert capfd.readouterr() == ('', '')


def test_get_project_name_fallback_broken_hgrc(testdir, capfd):
    testdir.tmpdir.ensure('.hg', 'hgrc').write('[paths]\ndefault = /')
    project_name = get_project_name()
    assert project_name.startswith('test_get_project_name_fallback')
    assert capfd.readouterr() == ('', '')


def test_parse_elasticsearch_storage():
    benchdir = os.path.basename(os.getcwd())

    assert parse_elasticsearch_storage('http://localhost:9200') == (['http://localhost:9200'], 'benchmark', 'benchmark', benchdir)
    assert parse_elasticsearch_storage('http://localhost:9200/benchmark2') == (
        ['http://localhost:9200'],
        'benchmark2',
        'benchmark',
        benchdir,
    )
    assert parse_elasticsearch_storage('http://localhost:9200/benchmark2/benchmark2') == (
        ['http://localhost:9200'],
        'benchmark2',
        'benchmark2',
        benchdir,
    )
    assert parse_elasticsearch_storage('http://host1:9200,host2:9200') == (
        ['http://host1:9200', 'http://host2:9200'],
        'benchmark',
        'benchmark',
        benchdir,
    )
    assert parse_elasticsearch_storage('http://host1:9200,host2:9200/benchmark2') == (
        ['http://host1:9200', 'http://host2:9200'],
        'benchmark2',
        'benchmark',
        benchdir,
    )
    assert parse_elasticsearch_storage('http://localhost:9200/benchmark2/benchmark2?project_name=project_name') == (
        ['http://localhost:9200'],
        'benchmark2',
        'benchmark2',
        'project_name',
    )
