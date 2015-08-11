import logging
import json

import py

from fields import Namespace

from pytest_benchmark.plugin import BenchmarkSession


class MockSession(BenchmarkSession):
    def __init__(self):
        self.histogram = True
        me = py.path.local(__file__)
        self.storage = me.dirpath(me.purebasename)
        self.benchmarks = []
        self.sort = u"min"
        self.compare = self.storage.join('0001_b692275e28a23b5d4aae70f453079ba593e60290_20150811_052350.json')
        self.logger = logging.getLogger(__name__)
        for bench_file in self.storage.listdir("[0-9][0-9][0-9][0-9]_*.json"):
            with bench_file.open() as fh:
                data = json.load(fh)
            self.benchmarks.extend(
                Namespace(
                    json=lambda: bench['stats'],
                    fullname=bench['fullname'],
                    **bench['stats']
                )
                for bench in data['benchmarks']
            )
            break


def test_rendering():
    sess = MockSession()
    sess.handle_histogram()
