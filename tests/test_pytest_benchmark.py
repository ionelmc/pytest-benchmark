from pytest_benchmark.__main__ import main

def test_main():
    assert main([]) == 0