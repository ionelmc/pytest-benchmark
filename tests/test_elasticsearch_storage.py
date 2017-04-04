from __future__ import absolute_import

import json
import logging
import os
from io import BytesIO
from io import StringIO

import elasticsearch
import py
import pytest
from freezegun import freeze_time

from pytest_benchmark import plugin
from pytest_benchmark.plugin import BenchmarkSession
from pytest_benchmark.plugin import pytest_benchmark_compare_machine_info
from pytest_benchmark.plugin import pytest_benchmark_generate_json
from pytest_benchmark.plugin import pytest_benchmark_group_stats
from pytest_benchmark.storage.elasticsearch import ElasticsearchStorage
from pytest_benchmark.storage.elasticsearch import _mask_hosts
from pytest_benchmark.utils import parse_elasticsearch_storage

try:
    import unittest.mock as mock
except ImportError:
    import mock

logger = logging.getLogger(__name__)

THIS = py.path.local(__file__)
BENCHFILE = THIS.dirpath('test_storage/0030_5b78858eb718649a31fb93d8dc96ca2cee41a4cd_20150815_030419_uncommitted-changes.json')
SAVE_DATA = json.load(BENCHFILE.open('rU'))
SAVE_DATA["machine_info"] = {'foo': 'bar'}
SAVE_DATA["commit_info"] = {'foo': 'bar'}

tmp = SAVE_DATA.copy()

ES_DATA = tmp.pop("benchmarks")[0]
ES_DATA.update(tmp)
ES_DATA["benchmark_id"] = "FoobarOS_commitId"


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.__dict__[item]


class LooseFileLike(BytesIO):
    def close(self):
        value = self.getvalue()
        super(LooseFileLike, self).close()
        self.getvalue = lambda: value


class MockStorage(ElasticsearchStorage):
    def __init__(self):
        self._es = mock.Mock(spec=elasticsearch.Elasticsearch)
        self._es_hosts = self._es_index = self._es_doctype = 'mocked'
        self.logger = logger
        self.default_machine_id = "FoobarOS"


class MockSession(BenchmarkSession):
    def __init__(self):
        self.verbose = False
        self.histogram = True
        self.benchmarks = []
        self.performance_regressions = []
        self.sort = u"min"
        self.compare = '0001'
        self.logger = logging.getLogger(__name__)
        self.machine_id = "FoobarOS"
        self.machine_info = {'foo': 'bar'}
        self.save = self.autosave = self.json = False
        self.options = {
            'min_rounds': 123,
            'min_time': 234,
            'max_time': 345,
        }
        self.compare_fail = []
        self.config = Namespace(hook=Namespace(
            pytest_benchmark_group_stats=pytest_benchmark_group_stats,
            pytest_benchmark_generate_machine_info=lambda **kwargs: {'foo': 'bar'},
            pytest_benchmark_update_machine_info=lambda **kwargs: None,
            pytest_benchmark_compare_machine_info=pytest_benchmark_compare_machine_info,
            pytest_benchmark_generate_json=pytest_benchmark_generate_json,
            pytest_benchmark_update_json=lambda **kwargs: None,
            pytest_benchmark_generate_commit_info=lambda **kwargs: {'foo': 'bar'},
            pytest_benchmark_update_commit_info=lambda **kwargs: None,
        ))
        self.elasticsearch_host = "localhost:9200"
        self.elasticsearch_index = "benchmark"
        self.elasticsearch_doctype = "benchmark"
        self.storage = MockStorage()
        self.group_by = 'group'
        self.columns = ['min', 'max', 'mean', 'stddev', 'median', 'iqr',
                        'outliers', 'rounds', 'iterations']
        self.benchmarks = []
        with BENCHFILE.open('rU') as fh:
            data = json.load(fh)
        self.benchmarks.extend(
            Namespace(
                as_dict=lambda include_data=False, stats=True, flat=False, _bench=bench:
                    dict(_bench, **_bench["stats"]) if flat else dict(_bench),
                name=bench['name'],
                fullname=bench['fullname'],
                group=bench['group'],
                options=bench['options'],
                has_error=False,
                params=None,
                **bench['stats']
            )
            for bench in data['benchmarks']
        )


try:
    text_type = unicode
except NameError:
    text_type = str


def force_text(text):
    if isinstance(text, text_type):
        return text
    else:
        return text.decode('utf-8')


def force_bytes(text):
    if isinstance(text, text_type):
        return text.encode('utf-8')
    else:
        return text


def make_logger(sess):
    output = StringIO()
    sess.logger = Namespace(
        warn=lambda code, text, **opts: output.write(u"%s: %s %s\n" % (code, force_text(text), opts)),
        info=lambda text, **opts: output.write(force_text(text) + u'\n'),
        error=lambda text: output.write(force_text(text) + u'\n'),
    )
    sess.storage.logger = Namespace(
        warn=lambda code, text, **opts: output.write(u"%s: %s %s\n" % (code, force_text(text), opts)),
        info=lambda text, **opts: output.write(force_text(text) + u'\n'),
        error=lambda text: output.write(force_text(text) + u'\n'),
    )
    return output


@pytest.fixture
def sess():
    return MockSession()


@pytest.fixture
def logger_output(sess):
    return make_logger(sess)


@freeze_time("2015-08-15T00:04:18.687119")
def test_handle_saving(sess, logger_output, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = "commitId"
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.handle_saving()
    sess.storage._es.index.assert_called_with(
        index='mocked',
        doc_type='mocked',
        body=ES_DATA,
        id='FoobarOS_commitId_tests/test_normal.py::test_xfast_parametrized[0]',
    )


def test_parse_with_no_creds():
    string = 'https://example.org,another.org'
    hosts, _, _, _ = parse_elasticsearch_storage(string)
    assert len(hosts) == 2
    assert 'https://example.org' in hosts
    assert 'https://another.org' in hosts


def test_parse_with_creds_in_first_host_of_url():
    string = 'https://user:pass@example.org,another.org'
    hosts, _, _, _ = parse_elasticsearch_storage(string)
    assert len(hosts) == 2
    assert 'https://user:pass@example.org' in hosts
    assert 'https://another.org' in hosts


def test_parse_with_creds_in_second_host_of_url():
    string = 'https://example.org,user:pass@another.org'
    hosts, _, _, _ = parse_elasticsearch_storage(string)
    assert len(hosts) == 2
    assert 'https://example.org' in hosts
    assert 'https://user:pass@another.org' in hosts


def test_parse_with_creds_in_netrc(tmpdir):
    netrc_file = os.path.join(tmpdir.strpath, 'netrc')
    with open(netrc_file, 'w') as f:
        f.write('machine example.org login user1 password pass1\n')
        f.write('machine another.org login user2 password pass2\n')
    string = 'https://example.org,another.org'
    hosts, _, _, _ = parse_elasticsearch_storage(string, netrc_file=netrc_file)
    assert len(hosts) == 2
    assert 'https://user1:pass1@example.org' in hosts
    assert 'https://user2:pass2@another.org' in hosts


def test_parse_url_creds_supersedes_netrc_creds(tmpdir):
    netrc_file = os.path.join(tmpdir.strpath, 'netrc')
    with open(netrc_file, 'w') as f:
        f.write('machine example.org login user1 password pass1\n')
        f.write('machine another.org login user2 password pass2\n')
    string = 'https://user3:pass3@example.org,another.org'
    hosts, _, _, _ = parse_elasticsearch_storage(string, netrc_file=netrc_file)
    assert len(hosts) == 2
    assert 'https://user3:pass3@example.org' in hosts  # superseded by creds in url
    assert 'https://user2:pass2@another.org' in hosts  # got creds from netrc file


def test__mask_hosts():
    hosts = ['https://user1:pass1@example.org', 'https://user2:pass2@another.org']
    masked_hosts = _mask_hosts(hosts)
    assert len(masked_hosts) == len(hosts)
    assert 'https://***:***@example.org' in masked_hosts
    assert 'https://***:***@another.org' in masked_hosts
