"""
Just to make sure the plugin doesn't choke on doctests::

    >>> print('Yay, doctests!')
    Yay, doctests!

"""
import time

def test_fast(benchmark):
    with benchmark:
        time.sleep(0.0001)
    assert 1 == 1

def test_slow(benchmark):
    with benchmark:
        time.sleep(0.001)
    assert 1 == 1

def test_slower(benchmark):
    with benchmark:
        time.sleep(0.01)
    assert 1 == 1
