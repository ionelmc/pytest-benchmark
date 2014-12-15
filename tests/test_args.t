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

Conflict between ``--benchmark-only`` and ``--benchmark-skip``::

  $ py.test -vv --benchmark-only --benchmark-skip tests.py
  ERROR: Can't have both --benchmark-only and --benchmark-skip options.
  [4]

With ``--benchmark-max-iterations``:

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
  ------* benchmark: 2 tests, 1 to 1 iterations, 0.5s max time ----* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* 1 (re)
  test_slow          .* 1 (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)

With ``--benchmark-max-time``::

  $ py.test -vv --doctest-modules --benchmark-max-time=0.000001 tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  -* benchmark: 2 tests, 5 to 5000 iterations, 0.000001s max time -* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* 5 (re)
  test_slow          .* 5 (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)

With ``--benchmark-disable-gc``::

  $ py.test -vv --doctest-modules --benchmark-disable-gc tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  ---* benchmark: 2 tests, 5 to 5000 iterations, 0.5s max time ----* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* (re)
  test_slow          .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)

With ``--benchmark-timer=time.time``::

  $ py.test -vv --doctest-modules --benchmark-timer=time.time tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  ---* benchmark: 2 tests, 5 to 5000 iterations, 0.5s max time ----* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* (re)
  test_slow          .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)

With ``--benchmark-timer=bogus``::

  $ py.test -vv --doctest-modules --benchmark-timer=bogus tests.py
  usage: py.test [options] [file_or_dir] [file_or_dir] [...]
  py.test: error: argument --benchmark-timer: Value for --benchmark-timer must be in dotted form. Eg: 'module.attr'.
  [2]

With ``--benchmark-scale=mean``::

  $ py.test -vv --doctest-modules --benchmark-scale=mean tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  ---* benchmark: 2 tests, 5 to 5000 iterations, 0.5s max time ----* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* (re)
  test_slow          .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)

With ``--benchmark-scale=bogus``::

  $ py.test -vv --doctest-modules --benchmark-scale=bogus tests.py
  usage: py.test [options] [file_or_dir] [file_or_dir] [...]
  py.test: error: argument --benchmark-scale: Value for --benchmark-scale must be one of: 'min', 'max', 'mean' or 'stddev'.
  [2]
