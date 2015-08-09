import time

import pytest


class Foo(object):
    def __init__(self, arg=0.01):
        self.arg = arg

    def run(self):
        self.internal(self.arg)

    def internal(self, duration):
        time.sleep(duration)


@pytest.mark.benchmark(max_time=0.001)
def test_weave_fixture(benchmark_weave):
    benchmark_weave(Foo.internal, lazy=True)
    f = Foo()
    f.run()


@pytest.mark.benchmark(max_time=0.001)
def test_weave_method(benchmark):
    benchmark.weave(Foo.internal, lazy=True)
    f = Foo()
    f.run()
