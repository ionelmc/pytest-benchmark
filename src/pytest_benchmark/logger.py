"""
..
  PYTEST_DONT_REWRITE
"""

import sys
import warnings

from _pytest._io import TerminalWriter
from pytest import PytestWarning  # noqa:PT013


class PytestBenchmarkWarning(PytestWarning):
    pass


class Logger:
    QUIET, NORMAL, VERBOSE = range(3)

    def __init__(self, level=NORMAL, config=None):
        self.level = level
        self.term = TerminalWriter(file=sys.stderr)
        self.suspend_capture = None
        self.resume_capture = None
        if config:
            capman = config.pluginmanager.getplugin('capturemanager')
            if capman:
                self.suspend_capture = getattr(capman, 'suspend_global_capture', getattr('capman', 'suspendcapture', None))
                self.resume_capture = getattr(capman, 'resume_global_capture', getattr('capman', 'resumecapture', None))

    def warning(self, text, warner=None, suspend=False):
        if self.level >= self.VERBOSE:
            if suspend and self.suspend_capture:
                self.suspend_capture(in_=True)
            self.term.line('')
            self.term.sep('-', red=True, bold=True)
            self.term.write(' WARNING: ', red=True, bold=True)
            self.term.line(text, red=True)
            self.term.sep('-', red=True, bold=True)
            if suspend and self.resume_capture:
                self.resume_capture()
        if warner is None:
            # These are informational messages about the plugin's own behavior (e.g. benchmarks
            # being auto-disabled), not warnings about the user's code, so they shouldn't be
            # promotable to errors by the user's `filterwarnings` setting. Doing so would abort
            # the whole session with an INTERNALERROR very early (during pytest_configure).
            # We can't use `warnings.catch_warnings()` here as it would also reset pytest's own
            # warnings-capturing state (breaking `-W`/`--benchmark-verbose` and the warnings
            # summary), so we push/pop a single filter entry instead.
            warnings.filterwarnings('always', category=PytestBenchmarkWarning)
            try:
                warnings.warn(PytestBenchmarkWarning(text), stacklevel=2)
            finally:
                warnings.filters.pop(0)
        else:
            warner(PytestBenchmarkWarning(text))

    def error(self, text):
        self.term.line('')
        self.term.sep('-', red=True, bold=True)
        self.term.line(text, red=True, bold=True)
        self.term.sep('-', red=True, bold=True)

    def info(self, text, newline=True, **kwargs):
        if self.level >= self.NORMAL:
            if not kwargs or kwargs == {'bold': True}:
                kwargs['purple'] = True
            if newline:
                self.term.line('')
            self.term.line(text, **kwargs)

    def debug(self, text, newline=False, **kwargs):
        if self.level >= self.VERBOSE:
            if self.suspend_capture:
                self.suspend_capture(in_=True)
            self.info(text, newline=newline, **kwargs)
            if self.resume_capture:
                self.resume_capture()
