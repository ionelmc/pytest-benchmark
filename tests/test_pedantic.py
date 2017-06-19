from pytest import mark
from pytest import raises


def test_single(benchmark):
    runs = []
    benchmark.pedantic(runs.append, args=[123])
    assert runs == [123]


def test_setup(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {"bar": 2}

    benchmark.pedantic(stuff, setup=setup)
    assert runs == [(1, 2)]


def test_args_kwargs(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    benchmark.pedantic(stuff, args=[1], kwargs={"bar": 2})
    assert runs == [(1, 2)]


def test_iterations(benchmark):
    runs = []

    benchmark.pedantic(runs.append, args=[1], iterations=10)
    assert runs == [1] * 11


def test_rounds_iterations(benchmark):
    runs = []

    benchmark.pedantic(runs.append, args=[1], iterations=10, rounds=15)
    assert runs == [1] * 151


def test_rounds(benchmark):
    runs = []

    benchmark.pedantic(runs.append, args=[1], rounds=15)
    assert runs == [1] * 15


def test_warmup_rounds(benchmark):
    runs = []

    benchmark.pedantic(runs.append, args=[1], warmup_rounds=15, rounds=5)
    assert runs == [1] * 20


@mark.parametrize("value", [0, "x"])
def test_rounds_must_be_int(benchmark, value):
    runs = []
    raises(ValueError, benchmark.pedantic, runs.append, args=[1], rounds=value)
    assert runs == []


@mark.parametrize("value", [-15, "x"])
def test_warmup_rounds_must_be_int(benchmark, value):
    runs = []
    raises(ValueError, benchmark.pedantic, runs.append, args=[1], warmup_rounds=value)
    assert runs == []


def test_setup_many_rounds(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {"bar": 2}

    benchmark.pedantic(stuff, setup=setup, rounds=10)
    assert runs == [(1, 2)] * 10


def test_cant_use_both_args_and_setup_with_return(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {"bar": 2}

    raises(TypeError, benchmark.pedantic, stuff, setup=setup, args=[123])
    assert runs == []


def test_can_use_both_args_and_setup_without_return(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    benchmark.pedantic(stuff, setup=lambda: None, args=[123])
    assert runs == [(123, 123)]


def test_cant_use_setup_with_many_iterations(benchmark):
    raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations=2)


@mark.parametrize("value", [0, -1, "asdf"])
def test_iterations_must_be_positive_int(benchmark, value):
    raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations=value)
