import time
from functools import partial

import pytest


class Foo(object):
    def __init__(self, arg=0.01):
        self.arg = arg

    def run(self):
        self.internal(self.arg)

    def internal(self, duration):
        time.sleep(duration)


def test_foo(benchmark_weave):
    with benchmark_weave(Foo.internal, lazy=True):
        f = Foo()
        f.run()
