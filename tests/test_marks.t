Ok::

  $ cat <<EOF > tests.py
  > import time
  > import pytest
  > @pytest.mark.benchmark(group="group-name", max_time=0.5, max_iterations=5000, min_iterations=5, timer=time.time, disable_gc=True)
  > def test_fast(benchmark):
  >     with benchmark:
  >         time.sleep(0.000001)
  >     assert 1 == 1
  > EOF

  $ py.test -vv --doctest-modules tests.py
  =====================* test session starts ======================* (re)
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 1 items
  \s* (re)
  tests.py::test_fast PASSED
  \s* (re)
  -* benchmark 'group-name': 1 tests, 5 to 5000 iterations, 0.5s max time -* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast             .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ====================* 1 passed in .* seconds ====================* (re)

Bogus args::

  $ cat <<EOF > testsborken.py
  > import time
  > import pytest
  > @pytest.mark.benchmark(
  >     group="group-name", max_time=0.5, max_iterations=5000,
  >     min_iterations=5, timer=time.time, disable_gc=True,
  >     only=True
  > )
  > def test_fast(benchmark):
  >     with benchmark:
  >         time.sleep(0.000001)
  >     assert 1 == 1
  > EOF


  $ py.test -vv --doctest-modules testsborken.py
  ============================= test session starts ==============================
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 1 items
  \s* (re)
  testsborken.py::test_fast ERROR
  \s* (re)
  ==================================== ERRORS ====================================
  _________________________ ERROR at setup of test_fast __________________________
  \s* (re)
  item = <Function 'test_fast'>
  \s* (re)
      def pytest_runtest_setup(item):
          benchmark = item.get_marker('benchmark')
          if benchmark:
              if benchmark.args:
                  raise ValueError("benchmark mark can't have positional arguments.")
              for name in benchmark.kwargs:
                  if name not in ('max_time', 'min_iterations', 'max_iterations', 'timer', 'group', 'disable_gc'):
  (>) *               raise ValueError\("benchmark mark can't have %r keyword argument." % name\) (re)
  E                   ValueError: benchmark mark can't have 'only' keyword argument.
  \s* (re)
  .*pytest_benchmark/plugin.py:.*: ValueError (re)
  ========================* 1 error in .* seconds =========================* (re)
  [1]
