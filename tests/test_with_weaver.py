import time
from collections.abc import Callable
from typing import Protocol

import pytest

from pytest_benchmark.fixture import BenchmarkFixture


class BenchmarkWeave(Protocol):
    def __call__(self, target: Callable[..., object], *, lazy: bool = False) -> None: ...


class Foo:
    def __init__(self, arg: float = 0.01) -> None:
        self.arg = arg

    def run(self) -> None:
        self.internal(self.arg)

    def internal(self, duration: float) -> None:
        time.sleep(duration)


@pytest.mark.benchmark(max_time=0.001)
def test_weave_fixture(benchmark_weave: BenchmarkWeave) -> None:
    benchmark_weave(Foo.internal, lazy=True)
    f = Foo()
    f.run()


@pytest.mark.benchmark(max_time=0.001)
def test_weave_method(benchmark: BenchmarkFixture) -> None:
    benchmark.weave(Foo.internal, lazy=True)
    f = Foo()
    f.run()
