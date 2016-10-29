import argparse
import distutils.spawn
import subprocess

import pytest
from pytest import mark

from pytest_benchmark.utils import clonefunc
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


@mark.parametrize('scm', ['git', 'hg'])
def test_get_commit_info(scm, testdir):
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

    testdir.makepyfile('asdf')
    subprocess.check_call([scm, 'add', 'test_get_commit_info.py'])
    subprocess.check_call([scm, 'commit', '-m', 'asdf'])
    out = get_commit_info()

    assert out.get('dirty') == False
    assert 'id' in out

    testdir.makepyfile('sadf')
    out = get_commit_info()

    assert out.get('dirty') == True
    assert 'id' in out


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
@mark.parametrize('set_remote', [True, False])
def test_get_project_name(scm, set_remote, testdir):
    if scm is None:
        assert get_project_name().startswith("test_get_project_name")
        return
    if not distutils.spawn.find_executable(scm):
        pytest.skip("%r not availabe on $PATH")
    subprocess.check_call([scm, 'init', '.'])
    if scm == 'git' and set_remote:
        subprocess.check_call('git config  remote.origin.url https://example.com/pytest_benchmark_repo.git'.split())
    elif scm == 'hg'and set_remote:
        testdir.tmpdir.join('.hg', 'hgrc').write("[ui]\n"
            "username = you <you@example.com>\n"
            "[paths]\n"
            "default = https://example.com/pytest_benchmark_repo\n"
                                                 )
    if set_remote:
        assert get_project_name() == "pytest_benchmark_repo"
    else:
        # use directory name if remote branch is not set
        assert get_project_name().startswith("test_get_project_name")


def test_parse_elasticsearch_storage():
    assert parse_elasticsearch_storage("http://localhost:9200") == (["http://localhost:9200"], "benchmark", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://localhost:9200/benchmark2") == (["http://localhost:9200"], "benchmark2", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://localhost:9200/benchmark2/benchmark2") == (["http://localhost:9200"], "benchmark2", "benchmark2", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://host1:9200,host2:9200") == (["http://host1:9200", "http://host2:9200"], "benchmark", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://host1:9200,host2:9200/benchmark2") == (["http://host1:9200", "http://host2:9200"], "benchmark2", "benchmark", "pytest-benchmark")
    assert parse_elasticsearch_storage("http://localhost:9200/benchmark2/benchmark2?project_name=project_name") == (["http://localhost:9200"], "benchmark2", "benchmark2", "project_name")
