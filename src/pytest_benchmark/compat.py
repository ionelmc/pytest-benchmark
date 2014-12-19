import sys

PY3 = sys.version_info[0] == 3

XRANGE = range if PY3 else xrange  # flake8: noqa
