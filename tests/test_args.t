With groups::

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
  >         time.sleep(0.1)
  >     assert 1 == 1
  > EOF

  $ py.test -vv --benchmark-only --benchmark-skip tests.py
  ERROR: Can't have both --benchmark-only and --benchmark-skip options.
  [4]

  $ py.test -vv --doctest-modules --benchmark-max-iterations=1 tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  ---* benchmark: 2 tests, 1 to 1 iterations, 0.5s max time ----* (re)
  Name \(time in .s\) * Min * Max * Avg * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast              .* 1 (re)
  test_slow              .* 1 (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)
