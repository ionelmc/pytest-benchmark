import time
import unittest

import pytest


class TerribleTerribleWayToWriteTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setupBenchmark(self, benchmark):
        self.benchmark = benchmark

    def test_foo(self):
        self.benchmark(time.sleep, 0.000001)


class TerribleTerribleWayToWritePatchTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def setupBenchmark(self, benchmark_weave):
        self.benchmark_weave = benchmark_weave

    def test_foo2(self):
        self.benchmark_weave('time.sleep')
        time.sleep(0.0000001)
