Ok::

  $ cat <<EOF > tests.py
  > import time
  > import pytest
  > @pytest.mark.benchmark(
  >     group="group-name",
  >     min_time=0.1,
  >     max_time=0.5,
  >     min_rounds=5,
  >     timer=time.time,
  >     disable_gc=True,
  >     warmup=False
  > )
  > def test_fast(benchmark):
  >     benchmark(lambda: time.sleep(0.000001))
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
  -* benchmark 'group-name': 1 tests, min 5 rounds (of min 0.1s), 1.0s max time, timer: .*-* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_fast             .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ====================* 1 passed in .* seconds ====================* (re)

Bogus args::

  $ cat <<EOF > testsborken.py
  > import time
  > import pytest
  > import functools
  > @pytest.mark.benchmark(
  >     group="group-name",
  >     min_time=0.1,
  >     max_time=0.5,
  >     min_rounds=5,
  >     timer=time.time,
  >     disable_gc=True,
  >     warmup=False,
  >     only=True,
  > )
  > def test_fast(benchmark):
  >     benchmark(functools.partial(time.sleep, 0.000001))
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
          benchmark = item.get_marker("benchmark")
          if benchmark:
              if benchmark.args:
                  raise ValueError("benchmark mark can't have positional arguments.")
              for name in benchmark.kwargs:
                  if name not in ("max_time", "min_iterations", "max_iterations", "timer", "group", "disable_gc"):
  (>) *               raise ValueError\("benchmark mark can't have %r keyword argument." % name\) (re)
  E                   ValueError: benchmark mark can't have 'only' keyword argument.
  \s* (re)
  .*pytest_benchmark/plugin.py:.*: ValueError (re)
  ========================* 1 error in .* seconds =========================* (re)
  [1]
