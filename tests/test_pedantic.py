from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Protocol

import pytest


class BenchmarkFixture(Protocol):
    def pedantic(
        self,
        target: Callable[..., object] | None,
        *,
        args: Sequence[object] | None = None,
        kwargs: Mapping[str, object] | None = None,
        setup: Callable[..., object] | None = None,
        teardown: Callable[..., object] | None = None,
        **options: object,
    ) -> object: ...


def test_single(benchmark: BenchmarkFixture):
    runs: list[object] = []
    benchmark.pedantic(runs.append, args=[123])
    assert runs == [123]


def test_setup(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {'bar': 2}

    benchmark.pedantic(stuff, setup=setup)
    assert runs == [(1, 2)]


def test_teardown(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=1234):
        runs.append((foo, bar))

    def teardown(foo, bar=1234):
        assert foo == 1
        assert bar == 2
        runs.append('teardown')

    benchmark.pedantic(stuff, args=[1], kwargs={'bar': 2}, teardown=teardown)
    assert runs == [(1, 2), 'teardown']


@pytest.mark.benchmark(cprofile=True)
def test_setup_cprofile(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {'bar': 2}

    benchmark.pedantic(stuff, setup=setup)
    assert runs == [(1, 2), (1, 2)]


@pytest.mark.benchmark(cprofile=True)
def test_teardown_cprofile(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff():
        runs.append('stuff')

    def teardown():
        runs.append('teardown')

    benchmark.pedantic(stuff, teardown=teardown)
    assert runs == ['stuff', 'teardown', 'stuff', 'teardown']

    runs: list[object] = []


def test_args_kwargs(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    benchmark.pedantic(stuff, args=[1], kwargs={'bar': 2})
    assert runs == [(1, 2)]


def test_iterations(benchmark: BenchmarkFixture):
    runs: list[object] = []

    benchmark.pedantic(runs.append, args=[1], iterations=10)
    assert runs == [1] * 11


def test_rounds_iterations(benchmark: BenchmarkFixture):
    runs: list[object] = []

    benchmark.pedantic(runs.append, args=[1], iterations=10, rounds=15)
    assert runs == [1] * 151


def test_rounds(benchmark: BenchmarkFixture):
    runs: list[object] = []

    benchmark.pedantic(runs.append, args=[1], rounds=15)
    assert runs == [1] * 15


def test_warmup_rounds(benchmark: BenchmarkFixture):
    runs: list[object] = []

    benchmark.pedantic(runs.append, args=[1], warmup_rounds=15, rounds=5)
    assert runs == [1] * 20


@pytest.mark.parametrize('value', [0, 'x'])
def test_rounds_must_be_int(benchmark: BenchmarkFixture, value):
    runs: list[object] = []
    pytest.raises(ValueError, benchmark.pedantic, runs.append, args=[1], rounds=value)
    assert runs == []


@pytest.mark.parametrize('value', [-15, 'x'])
def test_warmup_rounds_must_be_int(benchmark: BenchmarkFixture, value):
    runs: list[object] = []
    pytest.raises(ValueError, benchmark.pedantic, runs.append, args=[1], warmup_rounds=value)
    assert runs == []


def test_setup_many_rounds(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {'bar': 2}

    benchmark.pedantic(stuff, setup=setup, rounds=10)
    assert runs == [(1, 2)] * 10


def test_teardown_many_rounds(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff():
        runs.append('stuff')

    def teardown():
        runs.append('teardown')

    benchmark.pedantic(stuff, teardown=teardown, rounds=10)
    assert runs == ['stuff', 'teardown'] * 10


def test_teardown_many_iterations(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff():
        runs.append('stuff')

    def teardown():
        runs.append('teardown')

    benchmark.pedantic(stuff, teardown=teardown, iterations=3)
    assert runs == [
        'stuff',
        'stuff',
        'stuff',
        'teardown',  # first round
        'stuff',
        'teardown',  # computing the final result
    ]


def test_cant_use_both_args_and_setup_with_return(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {'bar': 2}

    pytest.raises(TypeError, benchmark.pedantic, stuff, setup=setup, args=[123])
    assert runs == []


def test_can_use_both_args_and_setup_without_return(benchmark: BenchmarkFixture):
    runs: list[object] = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    benchmark.pedantic(stuff, setup=lambda: None, args=[123])
    assert runs == [(123, 123)]


def test_cant_use_setup_with_many_iterations(benchmark: BenchmarkFixture):
    pytest.raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations=2)


@pytest.mark.parametrize('value', [0, -1, 'asdf'])
def test_iterations_must_be_positive_int(benchmark: BenchmarkFixture, value):
    pytest.raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations=value)
