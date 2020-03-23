from __future__ import absolute_import

import json
import logging
from io import BytesIO
from io import StringIO

import py
import pytest
from freezegun import freeze_time

from pytest_benchmark import plugin
from pytest_benchmark.plugin import BenchmarkSession
from pytest_benchmark.plugin import pytest_benchmark_compare_machine_info
from pytest_benchmark.plugin import pytest_benchmark_generate_json
from pytest_benchmark.plugin import pytest_benchmark_group_stats
from pytest_benchmark.storage.s3 import S3Storage

try:
    import unittest.mock as mock
except ImportError:
    import mock

logger = logging.getLogger(__name__)

THIS = py.path.local(__file__)
BENCHFILE = THIS.dirpath('test_storage/0030_5b78858eb718649a31fb93d8dc96ca2cee41a4cd_20150815_030419_uncommitted-changes.json')

SAVE_DATA = json.loads(BENCHFILE.read_text(encoding='utf8'))
SAVE_DATA["machine_info"] = {'foo': 'bar'}
SAVE_DATA["commit_info"] = {'foo': 'bar'}


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


class MockStorage(S3Storage):
    def __init__(self, *args, **kwargs):
        super(MockStorage, self).__init__(*args, **kwargs)
        m = mock.Mock()
        m.get_paginator.return_value.paginate.return_value = []
        m.head_object.return_value = False
        m.put_object.return_value = True
        self.client = m


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
        self.storage = MockStorage("s3://mocked/dir", default_machine_id="FoobarOS", logger=self.logger)
        self.group_by = 'group'
        self.columns = ['min', 'max', 'mean', 'stddev', 'median', 'iqr',
                        'outliers', 'rounds', 'iterations']
        self.benchmarks = []
        data = json.loads(BENCHFILE.read_text(encoding='utf8'))
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
        info=lambda text, **opts: output.write(force_text(text) + u'\n'),
        error=lambda text: output.write(force_text(text) + u'\n'),
    )
    sess.storage.logger = Namespace(
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
def test_handle_saving(sess, tmpdir, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = "commitId"
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.handle_saving()
    sess.storage.client.head_object.assert_called_with(
        Bucket='mocked',
        Key='dir/FoobarOS/0001_commitId.json',
    )

    args = sess.storage.client.put_object.call_args[1]
    assert args["Bucket"] == "mocked"
    assert args["Key"] == "dir/FoobarOS/0001_commitId.json"
    assert json.loads(args["Body"]) == SAVE_DATA


def test_s3_list_files():
    """Check if storage return the right next_num value."""
    m = mock.Mock()
    m.get_paginator.return_value.paginate.return_value = [
        {
            "ResponseMetadata": {"HTTPStatusCode": 200},
            "Contents": [
                {"Key": "FoobarOS/0001_commitId.json"},
                {"Key": "FoobarOS/0002_commitId.json"},
                {"Key": "FoobarOS/0003_commitId.json"},
                {"Key": "CentOS/0001_commitId.json"}
            ]
        }
    ]
    m.head_object.return_value = False
    storage = S3Storage(
        "s3://my-bucket",
        logging.getLogger(__name__),
        default_machine_id="FoobarOS",
        client=m
    )
    assert str(storage) == "s3://my-bucket"
    assert storage.location == "s3://my-bucket"
    assert storage._next_num == "0004"


def test_s3_load_single():
    """Test when loading only one benchmark."""
    m = mock.Mock()
    m.get_paginator.return_value.paginate.return_value = [
        {
            "ResponseMetadata": {"HTTPStatusCode": 200},
            "Contents": [
                {"Key": "FoobarOS/0001_commitId.json"},
                {"Key": "FoobarOS/0002_commitId.json"}
            ]
        }
    ]
    m.head_object.return_value = False
    m.get_object.return_value = {
        "Body": BytesIO(json.dumps(SAVE_DATA).encode())
    }
    storage = S3Storage(
        "s3://my-bucket",
        logging.getLogger(__name__),
        default_machine_id="FoobarOS",
        client=m
    )
    b = list(storage.load_benchmarks("0001"))
    assert b[0]["path"] == "s3://my-bucket/FoobarOS/0001_commitId.json"
    m.get_object.assert_called_once()


def test_s3_load_multi():
    """Test when loading multiple benchmark."""
    m = mock.Mock()
    m.get_paginator.return_value.paginate.return_value = [
        {
            "ResponseMetadata": {"HTTPStatusCode": 200},
            "Contents": [
                {"Key": "FoobarOS/0001_commitId.json"},
                {"Key": "FoobarOS/0002_commitId.json"},
                {"Key": "FoobarOS/0003_commitId.json"}
            ]
        }
    ]
    m.head_object.return_value = False
    m.get_object.side_effect = [
        {"Body": BytesIO(json.dumps(SAVE_DATA).encode())},
        {"Body": BytesIO(json.dumps(SAVE_DATA).encode())},
        {"Body": BytesIO(json.dumps(SAVE_DATA).encode())},
    ]

    storage = S3Storage(
        "s3://my-bucket",
        logging.getLogger(__name__),
        default_machine_id="FoobarOS",
        client=m
    )
    b = list(storage.load_benchmarks())
    assert len(b) == 3
    assert m.get_object.call_count == 3
