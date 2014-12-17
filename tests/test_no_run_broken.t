Test that we don't benchmark code that raises exceptions:

  $ cat <<EOF > tests.py
  > """
  >     >>> print('Yay, doctests!')
  >     Yay, doctests!
  > """
  > import time
  > import pytest
  > def test_bad(benchmark):
  >     with benchmark:
  >         raise Exception()
  >     assert 1 == 1
  > def test_bad2(benchmark):
  >     with benchmark:
  >         time.sleep(0.1)
  >     assert 1 == 0
  > @pytest.fixture(params=['a', 'b', 'c'])
  > def bad_fixture(request):
  >     raise ImportError()
  > def test_ok(benchmark, bad_fixture):
  >     with benchmark:
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
  tests.py:17: ImportError
  _________________________ ERROR at setup of test_ok[b] _________________________
  \s* (re)
  request = <SubRequest 'bad_fixture' for <Function 'test_ok[b]'>>
  \s* (re)
      @pytest.fixture(params=['a', 'b', 'c'])
      def bad_fixture(request):
  (>)       raise ImportError\(\) (re)
  E       ImportError
  \s* (re)
  tests.py:17: ImportError
  _________________________ ERROR at setup of test_ok[c] _________________________
  \s* (re)
  request = <SubRequest 'bad_fixture' for <Function 'test_ok[c]'>>
  \s* (re)
      @pytest.fixture(params=['a', 'b', 'c'])
      def bad_fixture(request):
  (>)       raise ImportError\(\) (re)
  E       ImportError
  \s* (re)
  tests.py:17: ImportError
  =================================== FAILURES ===================================
  ___________________________________ test_bad ___________________________________
  \s* (re)
  benchmark = <pytest_benchmark.plugin.Benchmark object at .*> (re)
  \s* (re)
      def test_bad(benchmark):
          with benchmark:
  (>)           raise Exception\(\) (re)
  E           Exception
  \s* (re)
  tests.py:9: Exception
  __________________________________ test_bad2 ___________________________________
  \s* (re)
  benchmark = <pytest_benchmark.plugin.Benchmark object at .*> (re)
  \s* (re)
      def test_bad2(benchmark):
          with benchmark:
              time.sleep(0.1)
  (>)       assert 1 == 0 (re)
  E       assert 1 == 0
  \s* (re)
  tests.py:14: AssertionError
  -* benchmark: 5 tests, 5 to 5000 iterations, 0.5s max time, timer: .*-* (re)
  Name \(time in us\) * Min * Max * Mean * StdDev * Iterations (re)
  -------------------------------------------------------------------------------
  test_bad            .* (re)
  test_bad2           .* (re)
  test_ok\[.\]          .* (re)
  test_ok\[.\]          .* (re)
  test_ok\[.\]          .* (re)
  -------------------------------------------------------------------------------
  \s* (re)
  ==================* 2 failed, 3 error in .* seconds ====================* (re)
  [1]
