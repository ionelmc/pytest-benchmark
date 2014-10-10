
def test_main(benchmark):
    with benchmark:
        range(1000000)
    assert 1 == 0
