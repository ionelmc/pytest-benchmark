import pytest


def test_skip(benchmark):
    pytest.skip('bla')
    benchmark(lambda: None)
