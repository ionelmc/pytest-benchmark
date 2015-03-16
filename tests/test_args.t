With groups::

  $ cat <<EOF > tests.py
  > """
  >     >>> print('Yay, doctests!')
  >     Yay, doctests!
  > """
  > import time
  > import pytest
  > def test_fast(benchmark):
  >     @benchmark
  >     def result():
  >         return time.sleep(0.000001)
  >     assert result == None
  > def test_slow(benchmark):
  >     benchmark(lambda: time.sleep(0.1))
  >     assert 1 == 1
  > EOF

Conflict between ``--benchmark-only`` and ``--benchmark-skip``::

  $ py.test -vv --benchmark-only --benchmark-skip tests.py
  ERROR: Can't have both --benchmark-only and --benchmark-skip options.
  [4]

With ``--benchmark-max-time``:

  $ py.test -vv --doctest-modules --benchmark-max-time=0.000001 --benchmark-min-rounds=1 tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  -* benchmark: 2 tests, min 1 rounds \(of min 25.00us\), 1.00us max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* 1  * \S+ (re)
  test_slow          .* 1  * \S+ (re)
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
  -* benchmark: 2 tests, min 5 rounds \(of min 25.00us\), 1.00us max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* 5  * \S+ (re)
  test_slow          .* 5  * \S+ (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)


With ``--benchmark-max-time=bogus``::

  $ py.test -vv --doctest-modules --benchmark-max-time=bogus tests.py
  usage: py.test [options] [file_or_dir] [file_or_dir] [...]
  py.test: error: argument --benchmark-max-time: Invalid decimal value 'bogus': InvalidOperation.* (re)
  [2]

With ``--benchmark-min-time=bogus``::

  $ py.test -vv --doctest-modules --benchmark-min-time=bogus tests.py
  usage: py.test [options] [file_or_dir] [file_or_dir] [...]
  py.test: error: argument --benchmark-min-time: Invalid decimal value 'bogus': InvalidOperation.* (re)
  [2]

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
  -* benchmark: 2 tests, min 5 rounds \(of min 25.00us\), 1.00s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
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
  -* benchmark: 2 tests, min 5 rounds \(of min 25.00us\), 1.00s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
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

With ``--benchmark-sort=mean``::

  $ py.test -vv --doctest-modules --benchmark-sort=mean tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 3 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  \s* (re)
  -* benchmark: 2 tests, min 5 rounds \(of min 25.00us\), 1.00s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* (re)
  test_slow          .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  =====================* 3 passed in .* seconds ===================* (re)

With ``--benchmark-sort=bogus``::

  $ py.test -vv --doctest-modules --benchmark-sort=bogus tests.py
  usage: py.test [options] [file_or_dir] [file_or_dir] [...]
  py.test: error: argument --benchmark-sort: Value for --benchmark-sort must be one of: 'min', 'max', 'mean' or 'stddev'.
  [2]

With xdist::

  $ if [ -n "$(py.test --version 2>&1 | grep xdist)" ]; then
  >   py.test --doctest-modules -n 1 tests.py
  > else
  >   echo "--------------------------------------------------------------------------------
  > WARNING: Benchmarks are automatically skipped because xdist plugin is active.Benchmarks cannot be performed reliably in a parallelized environment.
  > --------------------------------------------------------------------------------
  > ============================= test session starts ==============================
  > platform .*
  > plugins: .*
  > gw0 I
  > gw0 [3]
  > _
  > scheduling tests via LoadScheduling
  > .ss
  > ===================== 1 passed, 2 skipped in .* seconds ==================="
  > fi
  --------------------------------------------------------------------------------
  WARNING: Benchmarks are automatically skipped because xdist plugin is active.Benchmarks cannot be performed reliably in a parallelized environment.
  --------------------------------------------------------------------------------
  ============================= test session starts ==============================
  platform .* (re)
  plugins: .* (re)
  gw0 I
  gw0 [3]
  .* (re)
  scheduling tests via LoadScheduling
  .ss
  =====================* 1 passed, 2 skipped in .* seconds ===================* (re)
