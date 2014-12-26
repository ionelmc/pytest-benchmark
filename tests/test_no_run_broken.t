Test that we don't benchmark code that raises exceptions:

  $ cat <<EOF > tests.py
  > """
  >     >>> print('Yay, doctests!')
  >     Yay, doctests!
  > """
  > import time
  > import pytest
  > def test_bad(benchmark):
  >     @benchmark
  >     def result():
  >         raise Exception()
  >     assert 1 == 1
  > def test_bad2(benchmark):
  >     @benchmark
  >     def result():
  >         time.sleep(0.1)
  >     assert 1 == 0
  > @pytest.fixture(params=['a', 'b', 'c'])
  > def bad_fixture(request):
  >     raise ImportError()
  > def test_ok(benchmark, bad_fixture):
  >     @benchmark
  >     def result():
  >         time.sleep(0.1)
  >     assert 1 == 0
  > EOF

  $ py.test -vv tests.py
  ============================= test session starts ==============================
  platform .* (re)
  plugins: .* (re)
  collecting ... collected 5 items
  \s* (re)
  tests.py::test_bad FAILED
  tests.py::test_bad2 FAILED
  tests.py::test_ok[a] ERROR
  tests.py::test_ok[b] ERROR
  tests.py::test_ok[c] ERROR
  \s* (re)
  ==================================== ERRORS ====================================
  _________________________ ERROR at setup of test_ok[a] _________________________
  \s* (re)
  request = <SubRequest 'bad_fixture' for <Function 'test_ok[a]'>>
  \s* (re)
      @pytest.fixture(params=['a', 'b', 'c'])
      def bad_fixture(request):
  (>)       raise ImportError\(\) (re)
  E       ImportError
  \s* (re)
  tests.py:19: ImportError
  _________________________ ERROR at setup of test_ok[b] _________________________
  \s* (re)
  request = <SubRequest 'bad_fixture' for <Function 'test_ok[b]'>>
  \s* (re)
      @pytest.fixture(params=['a', 'b', 'c'])
      def bad_fixture(request):
  (>)       raise ImportError\(\) (re)
  E       ImportError
  \s* (re)
  tests.py:19: ImportError
  _________________________ ERROR at setup of test_ok[c] _________________________
  \s* (re)
  request = <SubRequest 'bad_fixture' for <Function 'test_ok[c]'>>
  \s* (re)
      @pytest.fixture(params=['a', 'b', 'c'])
      def bad_fixture(request):
  (>)       raise ImportError\(\) (re)
  E       ImportError
  \s* (re)
  tests.py:19: ImportError
  =================================== FAILURES ===================================
  ___________________________________ test_bad ___________________________________
  \s* (re)
  benchmark = <pytest_benchmark.plugin.BenchmarkFixture object at .*> (re)
  \s* (re)
      def test_bad(benchmark):
  (>)       @benchmark (re)
          def result():
              raise Exception()
  \s* (re)
  tests.py:.* (re)
  (_ )+ (re)
  .*pytest_benchmark/plugin.py:.*: in __call__ (re)
      duration, scale = self._calibrate_timer(runner)
  .*pytest_benchmark/plugin.py:.*: in _calibrate_timer (re)
      duration = runner(loops)
  .*pytest_benchmark/plugin.py:.*: in runner (re)
      function_to_benchmark()
  (_ )+ (re)
  \s* (re)
      @benchmark
      def result():
  (>)       raise Exception\(\) (re)
  E       Exception
  \s* (re)
  tests.py:10: Exception
  __________________________________ test_bad2 ___________________________________
  \s* (re)
  benchmark = <pytest_benchmark.plugin.BenchmarkFixture object at .*> (re)
  \s* (re)
      def test_bad2(benchmark):
          @benchmark
          def result():
              time.sleep(0.1)
  (>)       assert 1 == 0 (re)
  E       assert 1 == 0
  \s* (re)
  tests.py:16: AssertionError
  -* benchmark: 1 tests, min 5 rounds \(of min 25.00us\), 1.00s max time, timer: .* (re)
  Name \(time in .s\) * Min * Max * Mean * StdDev * Rounds * Iterations (re)
  -----------------------------------------------------------------* (re)
  test_bad2           .* (re)
  -----------------------------------------------------------------* (re)
  \s* (re)
  ==================* 2 failed, 3 error in .* seconds ====================* (re)
  [1]
