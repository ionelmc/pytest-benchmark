Simple::

  $ cat <<EOF > tests.py
  > """
  > Just to make sure the plugin doesn't choke on doctests::
  >     >>> print('Yay, doctests!')
  >     Yay, doctests!
  > """
  > import time
  > from functools import partial
  > import pytest
  > def test_fast(benchmark):
  >     @benchmark
  >     def result():
  >         return time.sleep(0.000001)
  >     assert result is None
  > def test_slow(benchmark):
  >     assert benchmark(partial(time.sleep, 0.001)) is None
  > def test_slower(benchmark):
  >     benchmark(lambda: time.sleep(0.01))
  > @pytest.mark.benchmark(min_rounds=2)
  > def test_xfast(benchmark):
  >     benchmark(str)
  > def test_fast(benchmark):
  >     benchmark(int)
  > EOF

  $ py.test -vv --doctest-modules tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_slow PASSED
  tests.py::test_slower PASSED
  tests.py::test_xfast PASSED
  tests.py::test_fast PASSED
  \s* (re)
  -* benchmark: 4 tests, min 5 rounds \(of min 0.1s\), 1.0s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_slow            .* (re)
  test_slower          .* (re)
  test_xfast           .* (re)
  test_fast            .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ====================* 5 passed in .* seconds ====================* (re)

Disabling benchmarks::

  $ py.test -vv --doctest-modules --benchmark-skip tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::[doctest] tests PASSED
  tests.py::test_slow SKIPPED
  tests.py::test_slower SKIPPED
  tests.py::test_xfast SKIPPED
  tests.py::test_fast SKIPPED
  \s* (re)
  ==============* 1 passed, 4 skipped in .* seconds ===============* (re)

Mark selection::

  $ py.test -vv --doctest-modules -m benchmark tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::test_xfast PASSED
  \s* (re)
  -* benchmark: 1 tests, min 5 rounds \(of min 0.1s\), 1.0s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_xfast        .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ===========* 4 tests deselected by "-m 'benchmark'" =============* (re)
  ============* 1 passed, 4 deselected in .* seconds ==============* (re)

Only run benchmarks::

  $ py.test -vv --doctest-modules --benchmark-only tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::[doctest] tests SKIPPED
  tests.py::test_slow PASSED
  tests.py::test_slower PASSED
  tests.py::test_xfast PASSED
  tests.py::test_fast PASSED
  \s* (re)
  -* benchmark: 4 tests, min 5 rounds \(of min 0.1s\), 1.0s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_slow         .* (re)
  test_slower       .* (re)
  test_xfast        .* (re)
  test_fast         .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ==============* 4 passed, 1 skipped in .* seconds ===============* (re)
