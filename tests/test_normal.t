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
  Name \(time in us\) * Min * Max * Avg * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast              .* (re)
  test_slow              .* (re)
  test_slower            .* (re)
  test_xfast             .* (re)
  ========================* 5 passed in .* seconds ========================* (re)

Disabling benchmarks::

  $ py.test -vv --doctest-modules --benchmark-skip tests.py
  ============================= test session starts ==============================
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast SKIPPED
  tests.py::test_slow SKIPPED
  tests.py::test_slower SKIPPED
  tests.py::test_xfast SKIPPED
  \s* (re)
  ===================== 1 passed, 4 skipped in .* seconds ==================* (re)

Mark selection::

  $ py.test -vv --doctest-modules -m benchmark tests.py
  ============================= test session starts ==============================
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::test_xfast PASSED
  \s* (re)
  ----------- benchmark: 1 tests, 5 to 5000 iterations, 0.5s max time ------------
  Name \(time in us\) * Min * Max * Avg * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_xfast             .* (re)
  ==================== 4 tests deselected by "-m 'benchmark'" ====================
  ==================* 1 passed, 4 deselected in .* seconds ==================* (re)
