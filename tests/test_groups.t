With groups::

  $ cat <<EOF > tests.py
  > """
  >     >>> print('Yay, doctests!')
  >     Yay, doctests!
  > """
  > import time
  > import pytest
  > def test_fast(benchmark):
  >     benchmark(lambda: time.sleep(0.000001))
  >     assert 1 == 1
  > def test_slow(benchmark):
  >     benchmark(lambda: time.sleep(0.001))
  >     assert 1 == 1
  > @pytest.mark.benchmark(group="A")
  > def test_slower(benchmark):
  >     benchmark(lambda: time.sleep(0.01))
  >     assert 1 == 1
  > @pytest.mark.benchmark(group="A", warmup=True)
  > def test_xfast(benchmark):
  >     benchmark(lambda: None)
  >     assert 1 == 1
  > EOF

  $ py.test -vv --doctest-modules tests.py | grep -v rootdir:
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::.*tests PASSED (re)
  tests.py::test_fast PASSED
  tests.py::test_slow PASSED
  tests.py::test_slower PASSED
  tests.py::test_xfast PASSED
  \s* (re)
  -* benchmark: 2 tests, min 5 rounds \(of min 25.00us\), 1.00s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast          .* (re)
  test_slow          .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  -* benchmark 'A': 2 tests, min 5 rounds \(of min 25.00us\), 1.00s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_slower        .* (re)
  test_xfast         .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ====================* 5 passed in .* seconds ====================* (re)
