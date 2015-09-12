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


def test_rounds_must_be_int(benchmark):
    runs = []

    raises(ValueError, benchmark.pedantic, runs.append, args=[1], rounds=0)
    raises(ValueError, benchmark.pedantic, runs.append, args=[1], rounds="x")
    assert runs == []

def test_warmup_rounds_must_be_int(benchmark):
    runs = []

    raises(ValueError, benchmark.pedantic, runs.append, args=[1], warmup_rounds=-15)
    raises(ValueError, benchmark.pedantic, runs.append, args=[1], warmup_rounds="x")
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


def test_iterations_must_be_positive_int(benchmark):
    raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations=0)
    raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations=-1)
    raises(ValueError, benchmark.pedantic, None, setup=lambda: None, iterations="asdf")
