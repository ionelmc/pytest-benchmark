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
