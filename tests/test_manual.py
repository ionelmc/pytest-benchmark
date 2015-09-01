from pytest import raises


def test_single(benchmark):
    runs = []
    benchmark.manual(runs.append, args=[123])
    assert runs == [123]


def test_setup(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {"bar": 2}

    benchmark.manual(stuff, setup=setup)
    assert runs == [(1, 2)]


def test_setup_many_rounds(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {"bar": 2}

    benchmark.manual(stuff, setup=setup, rounds=10)
    assert runs == [(1, 2)] * 10


def test_cant_use_both_args_and_setup_with_return(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    def setup():
        return [1], {"bar": 2}

    raises(TypeError, benchmark.manual, stuff, setup=setup, args=[123])
    assert runs == []


def test_can_use_both_args_and_setup_without_return(benchmark):
    runs = []

    def stuff(foo, bar=123):
        runs.append((foo, bar))

    benchmark.manual(stuff, setup=lambda: None, args=[123])
    assert runs == [(123, 123)]


def test_cant_use_setup_with_many_iterations(benchmark):
    raises(ValueError, benchmark.manual, None, setup=lambda: None, iterations=2)


def test_iterations_must_be_positive_int(benchmark):
    raises(ValueError, benchmark.manual, None, setup=lambda: None, iterations=0)
    raises(ValueError, benchmark.manual, None, setup=lambda: None, iterations=-1)
    raises(ValueError, benchmark.manual, None, setup=lambda: None, iterations="asdf")
