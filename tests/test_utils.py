from pytest import mark
from pytest_benchmark.utils import clonefunc

f1 = lambda a: a


def f2(a):
    return a


@mark.parametrize('f', [f1, f2])
def test_clonefunc(f):
    assert f(1) == clonefunc(f)(1)
    assert f(1) == clonefunc(f)(1)
