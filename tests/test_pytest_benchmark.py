import time

def test_main(benchmark):
    with benchmark:
        range(1000000)
        time.sleep(0.01)
    assert 1 == 1
