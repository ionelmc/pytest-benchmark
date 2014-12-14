Simple::
  $ cat <<EOF > tests.py
  > """
  >     >>> print('Yay, doctests!')
  >     Yay, doctests!
  > """
  > import time
  > import pytest
  > def test_fast(benchmark):
  >     with benchmark:
  >         time.sleep(0.000001)
  >     assert 1 == 1
  > def test_slow(benchmark):
  >     with benchmark:
  >         time.sleep(0.001)
  >     assert 1 == 1
  > def test_slower(benchmark):
  >     with benchmark:
  >         time.sleep(0.01)
  >     assert 1 == 1
  > @pytest.mark.benchmark(max_iterations=6000)
  > def test_xfast(benchmark):
  >     with benchmark:
  >         pass
  >     assert 1 == 1
  > EOF

  $ py.test -vv --doctest-modules tests.py
  ============================= test session starts ==============================
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  tests.py::test_slower PASSED
  tests.py::test_xfast PASSED
  \s* (re)
  ----------- benchmark: 4 tests, 5 to 5000 iterations, 0.5s max time ------------
  Name (time in us)            Min        Max        Avg       Mean     StdDev  Iterations
  ---------------------------------------------------------------------------------------
  test_fast              .* (re)
  test_slow              .* (re)
  test_slower            .* (re)
  test_xfast             .* (re)
  ========================* 5 passed in .* seconds ========================* (re)

Mark selection::

  $ py.test -vv --doctest-modules -m benchmark tests.py
  tests/test_normal.py::[doctest] test_normal PASSED
  tests/test_normal.py::test_fast PASSED
  tests/test_normal.py::test_slow PASSED
  tests/test_normal.py::test_slower PASSED
  tests/test_normal.py::test_xfast PASSED

  ----------- benchmark: 4 tests, 5 to 5000 iterations, 0.5s max time ------------
  Name (time in us)            Min        Max        Avg       Mean     StdDev  Iterations
  ---------------------------------------------------------------------------------------
  test_fast               3937.960   8955.956   7782.759   7782.759    697.300         66
  test_slow               3809.929   7987.022   6177.931   6177.931   1976.568         82
  test_slower            11896.133  18838.882  15613.752  15613.752   1277.672         34
  test_xfast                 0.000     20.027      1.101      1.101      0.574       6001
  ========================== 18 passed in 1.86 seconds ===========================
