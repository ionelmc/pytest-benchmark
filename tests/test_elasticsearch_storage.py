import json
import logging
from io import BytesIO
from io import StringIO
try:
    import unittest.mock as mock
except ImportError:
    import mock

import py
import pytest
from freezegun import freeze_time

from pytest_benchmark import plugin
from pytest_benchmark.plugin import BenchmarkSession
from pytest_benchmark.plugin import pytest_benchmark_compare_machine_info
from pytest_benchmark.plugin import pytest_benchmark_generate_json
from pytest_benchmark.plugin import pytest_benchmark_group_stats
from pytest_benchmark.report_backend import ElasticReportBackend
from pytest_benchmark.elasticsearch_storage import ElasticsearchStorage


THIS = py.path.local(__file__)
BENCHFILE = THIS.dirpath('test_storage/0030_5b78858eb718649a31fb93d8dc96ca2cee41a4cd_20150815_030419_uncommitted-changes.json')
SAVE_DATA = json.load(BENCHFILE.open('rU'))
SAVE_DATA["machine_info"] = {'foo': 'bar'}
SAVE_DATA["commit_info"] = {'foo': 'bar'}

tmp = SAVE_DATA.copy()

ES_DATA = tmp.pop("benchmarks")[0]
ES_DATA.update(tmp)


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


class MockElasticsearchReportBackend(ElasticReportBackend):
    def __init__(self, config):
        self.verbose = False
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.performance_regressions = []
        self.benchmarks = []
        self.machine_id = "FoobarOS"
        self.storage = mock.Mock(spec=ElasticsearchStorage)
        self.compare = '0001'
        self.save = self.autosave = self.json = False
        self.elasticsearch_hosts = ["localhost:9200"]
        self.elasticsearch_index = "benchmark"
        self.elasticsearch_doctype = "benchmark"


class MockSession(BenchmarkSession):
    def __init__(self):
        self.histogram = True
        self.benchmarks = []
        self.performance_regressions = []
        self.sort = u"min"
        self.logger = logging.getLogger(__name__)
        self.machine_id = "FoobarOS"
        self.machine_info = {'foo': 'bar'}
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
        self.report_backend = MockElasticsearchReportBackend(self.config)
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
    sess.report_backend.logger = Namespace(
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
    sess.report_backend.save = "commitId"
    sess.report_backend.autosave = True
    sess.report_backend.json = None
    sess.report_backend.save_data = False
    sess.report_backend.handle_saving(sess.benchmarks, sess.machine_info)
    sess.report_backend.storage.save.assert_called_with(ES_DATA, 'commitId_tests/test_normal.py::test_xfast_parametrized[0]')
