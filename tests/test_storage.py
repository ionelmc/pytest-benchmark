import json
import logging
import os
import sys
from io import BytesIO
from io import StringIO
from pathlib import Path

import py
import pytest
from freezegun import freeze_time

from pytest_benchmark import plugin
from pytest_benchmark.plugin import BenchmarkSession
from pytest_benchmark.plugin import pytest_benchmark_compare_machine_info
from pytest_benchmark.plugin import pytest_benchmark_generate_json
from pytest_benchmark.plugin import pytest_benchmark_group_stats
from pytest_benchmark.session import PerformanceRegression
from pytest_benchmark.storage.file import FileStorage
from pytest_benchmark.utils import NAME_FORMATTERS
from pytest_benchmark.utils import DifferenceRegressionCheck
from pytest_benchmark.utils import PercentageRegressionCheck
from pytest_benchmark.utils import get_machine_id

pytest_plugins = "pytester"


THIS = py.path.local(__file__)
STORAGE = THIS.dirpath(THIS.purebasename)

SAVE_DATA = json.load(STORAGE.listdir('0030_*.json')[0].open())
JSON_DATA = json.load(STORAGE.listdir('0030_*.json')[0].open())
SAVE_DATA["machine_info"] = JSON_DATA["machine_info"] = {'foo': 'bar'}
SAVE_DATA["commit_info"] = JSON_DATA["commit_info"] = {'foo': 'bar'}


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.__dict__[item]

    def getoption(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default


class LooseFileLike(BytesIO):
    def close(self):
        value = self.getvalue()
        super(LooseFileLike, self).close()
        self.getvalue = lambda: value


class MockSession(BenchmarkSession):
    def __init__(self, name_format):
        self.histogram = True
        self.verbose = False
        self.benchmarks = []
        self.performance_regressions = []
        self.sort = u"min"
        self.compare = '0001'
        self.logger = logging.getLogger(__name__)
        self.machine_id = "FoobarOS"
        self.machine_info = {'foo': 'bar'}
        self.save = self.autosave = self.json = False
        self.name_format = NAME_FORMATTERS[name_format]
        self.options = {
            'min_rounds': 123,
            'min_time': 234,
            'max_time': 345,
            'use_cprofile': False,
        }
        self.cprofile_sort_by = 'cumtime'
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
        self.storage = FileStorage(str(STORAGE), default_machine_id=get_machine_id(), logger=self.logger)
        self.group_by = 'group'
        self.columns = ['min', 'max', 'mean', 'stddev', 'median', 'iqr',
                        'outliers', 'rounds', 'iterations', 'ops']
        for bench_file in reversed(self.storage.query("[0-9][0-9][0-9][0-9]_*")):
            with bench_file.open('rU') as fh:
                data = json.load(fh)
            self.benchmarks.extend(
                Namespace(
                    as_dict=lambda include_data=False, stats=True, flat=False, _bench=bench, cprofile='cumtime':
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


@pytest.fixture(params=['short', 'normal', 'long'])
def name_format(request):
    return request.param


@pytest.fixture
def sess(request, name_format):
    return MockSession(name_format)


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


def test_rendering(sess):
    output = make_logger(sess)
    sess.histogram = os.path.join('docs', 'sample')
    sess.compare = '*/*'
    sess.sort = 'name'
    sess.handle_loading()
    sess.finish()
    sess.display(Namespace(
        ensure_newline=lambda: None,
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
        rewrite=lambda text, **opts: output.write(force_text(text)),
    ))


def test_regression_checks(sess, name_format):
    output = make_logger(sess)
    sess.handle_loading()
    sess.performance_regressions = []
    sess.compare_fail = [
        PercentageRegressionCheck("stddev", 5),
        DifferenceRegressionCheck("max", 0.000001)
    ]
    sess.finish()
    pytest.raises(PerformanceRegression, sess.display, Namespace(
        ensure_newline=lambda: None,
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
        rewrite=lambda text, **opts: output.write(force_text(text)),
    ))
    print(output.getvalue())
    assert sess.performance_regressions == {
        'normal': [
            ('test_xfast_parametrized[0] (0001_b87b9aa)',
             "Field 'stddev' has failed PercentageRegressionCheck: 23.331641765 > 5.000000000"),
            ('test_xfast_parametrized[0] (0001_b87b9aa)',
             "Field 'max' has failed DifferenceRegressionCheck: 0.000001843 > 0.000001000")
        ],
        'short': [
            ('xfast_parametrized[0] (0001)',
             "Field 'stddev' has failed PercentageRegressionCheck: 23.331641765 > 5.000000000"),
            ('xfast_parametrized[0] (0001)',
             "Field 'max' has failed DifferenceRegressionCheck: 0.000001843 > 0.000001000")
        ],
        'long': [
            ('tests/test_normal.py::test_xfast_parametrized[0] (0001_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190343_uncommitted-changes)',
             "Field 'stddev' has failed PercentageRegressionCheck: 23.331641765 > 5.000000000"),
            ('tests/test_normal.py::test_xfast_parametrized[0] (0001_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190343_uncommitted-changes)',
             "Field 'max' has failed DifferenceRegressionCheck: 0.000001843 > 0.000001000")
        ],
    }[name_format]
    output = make_logger(sess)
    pytest.raises(PerformanceRegression, sess.check_regressions)
    print(output.getvalue())
    assert output.getvalue() == {
        'short': """Performance has regressed:
\txfast_parametrized[0] (0001) - Field 'stddev' has failed PercentageRegressionCheck: 23.331641765 > 5.000000000
\txfast_parametrized[0] (0001) - Field 'max' has failed DifferenceRegressionCheck: 0.000001843 > 0.000001000
""",
        'normal': """Performance has regressed:
\ttest_xfast_parametrized[0] (0001_b87b9aa) - Field 'stddev' has failed PercentageRegressionCheck: 23.331641765 > 5.000000000
\ttest_xfast_parametrized[0] (0001_b87b9aa) - Field 'max' has failed DifferenceRegressionCheck: 0.000001843 > 0.000001000
""",
        'long': """Performance has regressed:
\ttests/test_normal.py::test_xfast_parametrized[0] (0001_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190343_uncommitted-changes) - Field 'stddev' has failed PercentageRegressionCheck: 23.331641765 > 5.000000000
\ttests/test_normal.py::test_xfast_parametrized[0] (0001_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190343_uncommitted-changes) - Field 'max' has failed DifferenceRegressionCheck: 0.000001843 > 0.000001000
"""
    }[name_format]


@pytest.mark.skipif(sys.version_info[:2] < (2, 7),
                    reason="Something weird going on, see: https://bugs.python.org/issue4482")
def test_regression_checks_inf(sess, name_format):
    output = make_logger(sess)
    sess.compare = '0002'
    sess.handle_loading()
    sess.performance_regressions = []
    sess.compare_fail = [
        PercentageRegressionCheck("stddev", 5),
        DifferenceRegressionCheck("max", 0.000001)
    ]
    sess.finish()
    pytest.raises(PerformanceRegression, sess.display, Namespace(
        ensure_newline=lambda: None,
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
        rewrite=lambda text, **opts: output.write(force_text(text)),
    ))
    print(output.getvalue())
    assert sess.performance_regressions == {
        'normal': [
            ('test_xfast_parametrized[0] (0002_b87b9aa)',
             "Field 'stddev' has failed PercentageRegressionCheck: inf > 5.000000000"),
            ('test_xfast_parametrized[0] (0002_b87b9aa)',
             "Field 'max' has failed DifferenceRegressionCheck: 0.000005551 > 0.000001000")
        ],
        'short': [
            ('xfast_parametrized[0] (0002)',
             "Field 'stddev' has failed PercentageRegressionCheck: inf > 5.000000000"),
            ('xfast_parametrized[0] (0002)',
             "Field 'max' has failed DifferenceRegressionCheck: 0.000005551 > 0.000001000")
        ],
        'long': [
            ('tests/test_normal.py::test_xfast_parametrized[0] '
             '(0002_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190348_uncommitted-changes)',
             "Field 'stddev' has failed PercentageRegressionCheck: inf > 5.000000000"),
            ('tests/test_normal.py::test_xfast_parametrized[0] '
             '(0002_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190348_uncommitted-changes)',
             "Field 'max' has failed DifferenceRegressionCheck: 0.000005551 > "
             '0.000001000')
        ]
    }[name_format]
    output = make_logger(sess)
    pytest.raises(PerformanceRegression, sess.check_regressions)
    print(output.getvalue())
    assert output.getvalue() == {
        'short': """Performance has regressed:
\txfast_parametrized[0] (0002) - Field 'stddev' has failed PercentageRegressionCheck: inf > 5.000000000
\txfast_parametrized[0] (0002) - Field 'max' has failed DifferenceRegressionCheck: 0.000005551 > 0.000001000
""",
        'normal': """Performance has regressed:
\ttest_xfast_parametrized[0] (0002_b87b9aa) - Field 'stddev' has failed PercentageRegressionCheck: inf > 5.000000000
\ttest_xfast_parametrized[0] (0002_b87b9aa) - Field 'max' has failed DifferenceRegressionCheck: 0.000005551 > 0.000001000
""",
        'long': """Performance has regressed:
\ttests/test_normal.py::test_xfast_parametrized[0] (0002_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190348_uncommitted-changes) - Field 'stddev' has failed PercentageRegressionCheck: inf > 5.000000000
\ttests/test_normal.py::test_xfast_parametrized[0] (0002_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190348_uncommitted-changes) - Field 'max' has failed DifferenceRegressionCheck: 0.000005551 > 0.000001000
"""
    }[name_format]


def test_compare_1(sess, LineMatcher):
    output = make_logger(sess)
    sess.handle_loading()
    sess.finish()
    sess.display(Namespace(
        ensure_newline=lambda: None,
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
        rewrite=lambda text, **opts: output.write(force_text(text)),
    ))
    print(output.getvalue())
    LineMatcher(output.getvalue().splitlines()).fnmatch_lines([
        'BENCHMARK-C6: Benchmark machine_info is different. Current: {foo: "bar"} VS saved: {machine: "x86_64", node: "minibox", processor: "x86_64", python_compiler: "GCC 4.6.3", python_implementation: "CPython", python_version: "2.7.3", release: "3.13.0-55-generic", system: "Linux"}. {\'fslocation\': \'tests*test_storage\'}',
        'Comparing against benchmarks from: 0001_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190343_uncommitted'
        '-changes.json',
        '',
        '*------------------------------------------------------------------------ benchmark: 2 tests -----------------------------------------------------------------------*',
        'Name (time in ns)               *      Min                 *Max                Mean              StdDev              Median                IQR            Outliers(*)  Rounds  Iterations  OPS (Mops/s) *',
        '--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------*',
        '*xfast_parametrized[[]0[]] (0001*)     217.3145 (1.0)      11*447.3891 (1.0)      262.2408 (1.00)     214.0442 (1.0)      220.1664 (1.00)     38.2154 (2.03)         90;1878    9987         418        3.8133 (1.00)*',
        '*xfast_parametrized[[]0[]] (NOW) *     217.9511 (1.00)     13*290.0380 (1.16)     261.2051 (1.0)      263.9842 (1.23)     220.1638 (1.0)      18.8080 (1.0)         160;1726    9710         431        3.8284 (1.0)*',
        '--------------------------------------------------------------------------------------------------------------------------------------------------------------------*',
        '(*) Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.',
        'OPS: Operations Per Second, computed as 1 / Mean',
    ])


def test_compare_2(sess, LineMatcher):
    output = make_logger(sess)
    sess.compare = '0002'
    sess.handle_loading()
    sess.finish()
    sess.display(Namespace(
        ensure_newline=lambda: None,
        write_line=lambda line, **opts: output.write(force_text(line) + u'\n'),
        section=lambda line, **opts: output.write(force_text(line) + u'\n'),
        write=lambda text, **opts: output.write(force_text(text)),
        rewrite=lambda text, **opts: output.write(force_text(text)),
    ))
    print(output.getvalue())
    LineMatcher(output.getvalue().splitlines()).fnmatch_lines([
        'BENCHMARK-C6: Benchmark machine_info is different. Current: {foo: "bar"} VS saved: {machine: "x86_64", node: "minibox", processor: "x86_64", python_compiler: "GCC 4.6.3", python_implementation: "CPython", python_version: "2.7.3", release: "3.13.0-55-generic", system: "Linux"}. {\'fslocation\': \'tests*test_storage\'}',
        'Comparing against benchmarks from: 0002_b87b9aae14ff14a7887a6bbaa9731b9a8760555d_20150814_190348_uncommitted-changes.json',
        '',
        '*------------------------------------------------------------------------ benchmark: 2 tests -----------------------------------------------------------------------*',
        'Name (time in ns)            *         Min                 *Max                Mean              StdDev              Median                IQR            Outliers(*)  Rounds  Iterations  OPS (Mops/s)*',
        '--------------------------------------------------------------------------------------------------------------------------------------------------------------------*',
        '*xfast_parametrized[[]0[]] (0002*)     216.9028 (1.0)       7*739.2997 (1.0)      254.0585 (1.0)        0.0000 (1.0)      219.8103 (1.0)      27.3309 (1.45)        235;1688   11009         410        3.9361 (1.0)*',
        '*xfast_parametrized[[]0[]] (NOW) *     217.9511 (1.00)     13*290.0380 (1.72)     261.2051 (1.03)     263.9842 (inf)      220.1638 (1.00)     18.8080 (1.0)         160;1726    9710         431        3.8284 (0.97)*',
        '--------------------------------------------------------------------------------------------------------------------------------------------------------------------*',
        '(*) Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.',
        'OPS: Operations Per Second, computed as 1 / Mean',
    ])

@freeze_time("2015-08-15T00:04:18.687119")
def test_save_json(sess, tmpdir, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = False
    sess.autosave = False
    sess.json = LooseFileLike()
    sess.save_data = False
    sess.handle_saving()
    assert tmpdir.listdir() == []
    assert json.loads(sess.json.getvalue().decode()) == JSON_DATA


@freeze_time("2015-08-15T00:04:18.687119")
def test_save_with_name(sess, tmpdir, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = 'foobar'
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage.path = Path(str(tmpdir))
    sess.handle_saving()
    files = list(Path(str(tmpdir)).rglob('*.json'))
    print(files)
    assert len(files) == 1
    assert json.load(files[0].open('rU')) == SAVE_DATA


@freeze_time("2015-08-15T00:04:18.687119")
def test_save_no_name(sess, tmpdir, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = True
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage.path = Path(str(tmpdir))
    sess.handle_saving()
    files = list(Path(str(tmpdir)).rglob('*.json'))
    assert len(files) == 1
    assert json.load(files[0].open('rU')) == SAVE_DATA


@freeze_time("2015-08-15T00:04:18.687119")
def test_save_with_error(sess, tmpdir, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = True
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage.path = Path(str(tmpdir))
    for bench in sess.benchmarks:
        bench.has_error = True
    sess.handle_saving()
    files = list(Path(str(tmpdir)).rglob('*.json'))
    assert len(files) == 1
    assert json.load(files[0].open('rU')) == {
        'benchmarks': [],
        'commit_info': {'foo': 'bar'},
        'datetime': '2015-08-15T00:04:18.687119',
        'machine_info': {'foo': 'bar'},
        'version': '2.5.0'
    }


@freeze_time("2015-08-15T00:04:18.687119")
def test_autosave(sess, tmpdir, monkeypatch):
    monkeypatch.setattr(plugin, '__version__', '2.5.0')
    sess.save = False
    sess.autosave = True
    sess.json = None
    sess.save_data = False
    sess.storage.path = Path(str(tmpdir))
    sess.handle_saving()
    files = list(Path(str(tmpdir)).rglob('*.json'))
    assert len(files) == 1
    assert json.load(files[0].open('rU')) == SAVE_DATA
