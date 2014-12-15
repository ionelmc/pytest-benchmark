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
  >         time.sleep(0.001)
  >     assert 1 == 1
  > @pytest.mark.benchmark(group="A")
  > def test_slower(benchmark):
  >     with benchmark:
  >         time.sleep(0.01)
  >     assert 1 == 1
  > @pytest.mark.benchmark(group="A", max_iterations=6000)
  > def test_xfast(benchmark):
  >     with benchmark:
  >         pass
  >     assert 1 == 1
  > EOF

  $ py.test -vv --doctest-modules tests.py
  =====================* test session starts ======================* (re)
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
  ----* benchmark: 2 tests, 5 to 5000 iterations, 0.5s max time ---* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* (re)
  test_slow          .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  --* benchmark 'A': 2 tests, 5 to 5000 iterations, 0.5s max time -* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_slower        .* (re)
  test_xfast         .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ====================* 5 passed in .* seconds ====================* (re)
