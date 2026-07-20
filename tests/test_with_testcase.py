import time
import unittest
from collections.abc import Callable
from typing import Protocol

import pytest

from pytest_benchmark.fixture import BenchmarkFixture


class BenchmarkWeave(Protocol):
    def __call__(self, target: str | Callable[..., object], *, lazy: bool = False) -> None: ...


class TerribleTerribleWayToWriteTests(unittest.TestCase):
    benchmark: BenchmarkFixture

    @pytest.fixture(autouse=True)
    def setupBenchmark(self, benchmark: BenchmarkFixture) -> None:
        self.benchmark = benchmark

    def test_foo(self):
        self.benchmark(time.sleep, 0.000001)


class TerribleTerribleWayToWritePatchTests(unittest.TestCase):
    benchmark_weave: BenchmarkWeave

    @pytest.fixture(autouse=True)
    def setupBenchmark(self, benchmark_weave: BenchmarkWeave) -> None:
        self.benchmark_weave = benchmark_weave

    def test_foo2(self):
        self.benchmark_weave('time.sleep')
        time.sleep(0.0000001)
