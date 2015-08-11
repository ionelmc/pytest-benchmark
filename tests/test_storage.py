import json
import logging

import py
import pytest

from freezegun import freeze_time

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

from pytest_benchmark.plugin import BenchmarkSession, PerformanceRegression
from pytest_benchmark.plugin import pytest_benchmark_compare_machine_info
from pytest_benchmark.plugin import pytest_benchmark_generate_json
from pytest_benchmark.plugin import pytest_benchmark_group_stats
from pytest_benchmark.utils import PercentageRegressionCheck, DifferenceRegressionCheck

SAVE_DATA = {
    "commit_info": {
        'foo': 'bar',
    },
    "version": "2.5.0",
    "benchmarks": [
        {
            "stats": {
                'include_data': False,
                "q1": 19.35233497619629,
                "q3": 20.36447501182556,
                "iterations": 1,
                "min": 19.316043853759766,
                "max": 21.620103120803833,
                "median": 19.9351589679718,
                "iqr": 1.0121400356292725,
                "stddev_outliers": 2,
                "stddev": 0.7074680670532808,
                "outliers": "2;0",
                "iqr_outliers": 0,
                "rounds": 10,
                "mean": 20.049841284751892
            },
            "fullname": "tests/test_func/test_perf.py::test_engine",
            "group": None,
            "name": "test_engine",
            "options": {
                "disable_gc": False,
                "warmup": False,
                "timer": "time",
                "min_rounds": 10,
                "max_time": 1.0,
                "min_time": 2.5e-05
            }
        }
    ],
    "machine_info": {
        "foo": "bar",
    },
    "datetime": "2012-01-14T12:00:01"
}
JSON_DATA = {
    "commit_info": {
        'foo': 'bar',
    },
    "version": "2.5.0",
    "benchmarks": [
        {
            "stats": {
                'include_data': True,
                "q1": 19.35233497619629,
                "q3": 20.36447501182556,
                "iterations": 1,
                "min": 19.316043853759766,
                "max": 21.620103120803833,
                "median": 19.9351589679718,
                "iqr": 1.0121400356292725,
                "stddev_outliers": 2,
                "stddev": 0.7074680670532808,
                "outliers": "2;0",
                "iqr_outliers": 0,
                "rounds": 10,
                "mean": 20.049841284751892
            },
            "fullname": "tests/test_func/test_perf.py::test_engine",
            "group": None,
            "name": "test_engine",
            "options": {
                "disable_gc": False,
                "warmup": False,
                "timer": "time",
                "min_rounds": 10,
                "max_time": 1.0,
                "min_time": 2.5e-05
            }
        }
    ],
    "machine_info": {
        "foo": "bar",
    },
    "datetime": "2012-01-14T12:00:01"
}


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.__dict__[item]


class TestFriendlyStringIO(StringIO):
    def close(self):
        value = self.getvalue()
        super(TestFriendlyStringIO, self).close()
        self.getvalue = lambda: value


class MockSession(BenchmarkSession):
    def __init__(self):
        self.histogram = True
        me = py.path.local(__file__)
        self.storage = me.dirpath(me.purebasename)
        self.benchmarks = []
        self.sort = u"min"
        self.compare = self.storage.join('0001_b692275e28a23b5d4aae70f453079ba593e60290_20150811_052350.json')
        self.logger = logging.getLogger(__name__)
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
        self.group_by = 'group'
        for bench_file in self.storage.listdir("[0-9][0-9][0-9][0-9]_*.json"):
            with bench_file.open('rU') as fh:
                data = json.load(fh)
            self.benchmarks.extend(
                Namespace(
                    json=lambda include_data=False: dict(bench['stats'], include_data=include_data),
                    name=bench['name'],
                    fullname=bench['fullname'],
                    group=bench['group'],
                    options=bench['options'],
                    **bench['stats']
                )
                for bench in data['benchmarks']
            )
            break


@pytest.fixture
def sess(request):
    return MockSession()


def make_logger(sess):
    output = StringIO()
    sess.logger = Namespace(
        warn=lambda text: output.write(text + '\n'),
        info=lambda text, **opts: output.write(text + '\n'),
        error=lambda text: output.write(text + '\n'),
    )
    return output


def test_rendering(sess):
    sess.handle_histogram()


def test_regression_checks(sess):
    output = make_logger(sess)
    sess.handle_loading()
    sess.compare == '0001'
    sess.performance_regressions = []
    sess.compare_fail = [
        PercentageRegressionCheck("stddev", 5),
        DifferenceRegressionCheck("max", 0.5)
    ]
    sess.display_results_table(Namespace(
        write_line=lambda line, **opts: output.write(line + '\n'),
        write=lambda text, **opts: output.write(text),
    ))
    assert sess.performance_regressions == [
        ('tests/test_func/test_perf.py::test_engine',
         'Field stddev has failed PercentageRegressionCheck: 26.572963937 > '
         '5.000000000'),
        ('tests/test_func/test_perf.py::test_engine',
         'Field max has failed DifferenceRegressionCheck: 0.617182970 > 0.500000000')
    ]
    output = make_logger(sess)
    pytest.raises(PerformanceRegression, sess.check_regressions)
    assert output.getvalue() == """Performance has regressed:
\ttests/test_func/test_perf.py::test_engine - Field stddev has failed PercentageRegressionCheck: 26.572963937 \
> 5.000000000
\ttests/test_func/test_perf.py::test_engine - Field max has failed DifferenceRegressionCheck: 0.617182970 > \
0.500000000
"""



def test_compare(sess):
    output = make_logger(sess)
    sess.handle_loading()
    sess.display_results_table(Namespace(
        write_line=lambda line, **opts: output.write(line + '\n'),
        write=lambda text, **opts: output.write(text),
    ))
    assert output.getvalue() == (
        "Benchmark machine_info is different. Current: {foo: 'bar'} VS saved: {"
        "machine: 'x86_64', node: 'jenkins', processor: 'x86_64', python_compiler: 'GCC 4.6.3', "
        "python_implementation: 'CPython', python_version: '2.7.3', release: '3.13.0-53-generic', system: 'Linux'}.\n"
        "Comparing against benchmark 0001_b692275e28a23b5d4aae70f453079ba593e60290_20150811_052350.json:\n"
        "| commit info: {dirty: False, id: 'b692275e28a23b5d4aae70f453079ba593e60290'}\n"
        "| saved at: 2015-08-11T02:23:50.661428\n"
        "| saved using pytest-benchmark 2.5.0:\n"
        "-------------------------------------- benchmark: 1 tests, min 123 rounds (of min 234), "
        "345 max time, timer: None --------------------------------------\n"
        "Name (time in s)         Min              Max             Mean          StdDev           Median             "
        "IQR          Outliers(*)  Rounds  Iterations\n"
        "--------------------------------------------------------------------------------------------------------------"
        "------------------------------------------\n"
        "test_engine          19.3160          21.6201          20.0498          0.7075          19.9352          "
        "1.0121                  2;0      10           1\n"
        "                     -0.0062 (0%)     +0.6172 (2%)     +0.0157 (0%)    +0.1485 (26%)    +0.0806 (0%)    "
        "+0.3144 (45%)            4;0      10           1\n"
        "--------------------------------------------------------------------------------------------------------------"
        "------------------------------------------\n"
        "(*) Outliers: 1 Standard Deviation from Mean; "
        "1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.\n"
        "\n"
    )


@freeze_time("2012-01-14 12:00:01")
def test_save_json(sess, tmpdir):
    sess.save = False
    sess.autosave = False
    sess.json = TestFriendlyStringIO()
    sess.save_data = False
    sess.handle_saving()
    assert tmpdir.listdir() == []
    assert json.loads(sess.json.getvalue()) == JSON_DATA


@freeze_time("2012-01-14 12:00:01")
def test_save_with_name(sess, tmpdir):
    sess.save = 'foobar'
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage = tmpdir
    sess.handle_saving()
    files = tmpdir.listdir()
    assert len(files) == 1
    assert json.loads(files[0].read()) == SAVE_DATA


@freeze_time("2012-01-14 12:00:01")
def test_save_no_name(sess, tmpdir):
    sess.save = True
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage = tmpdir
    sess.handle_saving()
    files = tmpdir.listdir()
    assert len(files) == 1
    assert json.loads(files[0].read()) == SAVE_DATA


@freeze_time("2012-01-14 12:00:01")
def test_autosave(sess, tmpdir):
    sess.save = False
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage = tmpdir
    sess.handle_saving()
    files = tmpdir.listdir()
    assert len(files) == 1
    assert json.loads(files[0].read()) == SAVE_DATA
