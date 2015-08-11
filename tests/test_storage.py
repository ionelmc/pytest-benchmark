import logging
import json

try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

import py
import pytest

from pytest_benchmark.plugin import BenchmarkSession, pytest_benchmark_group_stats, pytest_benchmark_compare_machine_info


class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, item):
        return self.__dict__[item]

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
        ))
        self.group_by = 'group'
        for bench_file in self.storage.listdir("[0-9][0-9][0-9][0-9]_*.json"):
            with bench_file.open('rU') as fh:
                data = json.load(fh)
            self.benchmarks.extend(
                Namespace(
                    json=lambda: bench['stats'],
                    name=bench['name'],
                    fullname=bench['fullname'],
                    group=bench['group'],
                    **bench['stats']
                )
                for bench in data['benchmarks']
            )
            break


@pytest.fixture
def sess(request):
    return MockSession()


def test_rendering(sess):
    sess.handle_histogram()


def test_compare(sess):
    # self.handle_saving()
    # self.handle_loading()
    # self.display_results_table(tr)
    # self.check_regressions()
    # self.handle_histogram()
    output = StringIO()
    sess.logger = Namespace(
        warn=lambda text: output.write(text + '\n'),
        info=lambda text, **opts: output.write(text + '\n'),
    )
    sess.handle_loading()
    sess.display_results_table(Namespace(
        write_line=lambda line, **opts: output.write(line + '\n'),
        write=lambda text, **opts: output.write(text),
    ))
    assert output.getvalue() == """Benchmark machine_info is different. Current: {foo: 'bar'} VS saved: {machine: 'x86_64', node: 'jenkins', processor: 'x86_64', python_compiler: 'GCC 4.6.3', python_implementation: 'CPython', python_version: '2.7.3', release: '3.13.0-53-generic', system: 'Linux'}.
Comparing against benchmark 0001_b692275e28a23b5d4aae70f453079ba593e60290_20150811_052350.json:
| commit info: {dirty: False, id: 'b692275e28a23b5d4aae70f453079ba593e60290'}
| saved at: 2015-08-11T02:23:50.661428
| saved using pytest-benchmark 2.5.0:
-------------------------------------- benchmark: 1 tests, min 123 rounds (of min 234), 345 max time, timer: None --------------------------------------
Name (time in s)         Min              Max             Mean          StdDev           Median             IQR          Outliers(*)  Rounds  Iterations
--------------------------------------------------------------------------------------------------------------------------------------------------------
test_engine          19.3160          21.6201          20.0498          0.7075          19.9352          1.0121                  2;0      10           1
                     -0.0062 (0%)     +0.6172 (2%)     +0.0157 (0%)    +0.1485 (26%)    +0.0806 (0%)    +0.3144 (45%)            4;0      10           1
--------------------------------------------------------------------------------------------------------------------------------------------------------
(*) Outliers: 1 Standard Deviation from Mean; 1.5 IQR (InterQuartile Range) from 1st Quartile and 3rd Quartile.

"""
