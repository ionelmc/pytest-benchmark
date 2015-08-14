import json
import os
import logging
from io import StringIO, BytesIO

import py
import pytest
from freezegun import freeze_time

from pytest_benchmark.plugin import BenchmarkSession, PerformanceRegression
from pytest_benchmark.plugin import pytest_benchmark_compare_machine_info
from pytest_benchmark.plugin import pytest_benchmark_generate_json
from pytest_benchmark.plugin import pytest_benchmark_group_stats
from pytest_benchmark.utils import PercentageRegressionCheck, DifferenceRegressionCheck

THIS = py.path.local(__file__)
STORAGE = THIS.dirpath(THIS.purebasename)

SAVE_DATA = json.load(STORAGE.listdir('0030_*.json')[0].open())
SAVE_DATA["benchmarks"][0]["stats"]["include_data"] = False
JSON_DATA = json.load(STORAGE.listdir('0030_*.json')[0].open())
JSON_DATA["benchmarks"][0]["stats"]["include_data"] = True


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.__dict__[item]


class TestFriendlyFileLike(BytesIO):
    def close(self):
        value = self.getvalue()
        super(TestFriendlyFileLike, self).close()
        self.getvalue = lambda: value


class MockSession(BenchmarkSession):
    def __init__(self):
        self.histogram = True
        self.storage = STORAGE
        self.benchmarks = []
        self.sort = u"min"
        self.compare = '0001'
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
        for bench_file in reversed(self.storage.listdir("[0-9][0-9][0-9][0-9]_*.json", sort=True)):
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


@pytest.fixture
def sess(request):
    return MockSession()


def make_logger(sess):
    output = StringIO()
    sess.logger = Namespace(
        warn=lambda text: output.write(force_text(text) + u'\n'),
        info=lambda text, **opts: output.write(force_text(text) + u'\n'),
        error=lambda text: output.write(force_text(text) + u'\n'),
    )
    return output


def test_rendering(sess):
    sess.histogram = os.path.join('docs', 'sample')
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
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
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
    print(output.getvalue())
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
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
    ))
    print(output.getvalue())
    assert output.getvalue() == """Benchmark machine_info is different. Current: {foo: "bar"} VS saved: {machine: "x86_64", node: "minibox", processor: "x86_64", python_compiler: "GCC 4.6.3", python_implementation: "CPython", python_version: "2.7.3", release: "3.13.0-55-generic", system: "Linux"}.
Comparing against benchmark 0001_001f2d07786d4f90b406372dba594658a43a2558_20150814_181653_uncommitted-changes.json:
| commit info: {dirty: true, id: "001f2d07786d4f90b406372dba594658a43a2558"}
| saved at: 2015-08-14T15:16:53.144088
| saved using pytest-benchmark 2.5.0:
------------------------------------------- benchmark: 1 tests, min 123 rounds (of min 234), 345 max time, timer: None -------------------------------------------
Name (time in ns)                  Min              Max             Mean          StdDev           Median             IQR          Outliers(*)  Rounds  Iterations
------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_xfast_parametrized[0]     72.9561          82.9697          75.0167          3.2819          73.9098          2.1458                  2;2      14        1000
                                    NC          -2.1458 (2%)     -0.3406 (0%)    -0.2748 (7%)          NC         +1.9073 (800%)           2;4      14        1000
------------------------------------------------------------------------------------------------------------------------------------------------------------------
(*) Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.

"""


@freeze_time("2012-01-14 12:00:01")
def test_save_json(sess, tmpdir):
    sess.save = False
    sess.autosave = False
    sess.json = TestFriendlyFileLike()
    sess.save_data = False
    sess.handle_saving()
    assert tmpdir.listdir() == []
    assert json.loads(sess.json.getvalue().decode()) == JSON_DATA


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
    assert json.load(files[0].open('rU')) == SAVE_DATA


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
    assert json.load(files[0].open('rU')) == SAVE_DATA


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
    assert json.load(files[0].open('rU')) == SAVE_DATA
