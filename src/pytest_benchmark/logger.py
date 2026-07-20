"""
..
  PYTEST_DONT_REWRITE
"""

import sys
import warnings
from collections.abc import Callable

import pytest
from _pytest._io import TerminalWriter
from pytest import PytestWarning  # noqa:PT013


class PytestBenchmarkWarning(PytestWarning):
    pass


class Logger:
    QUIET, NORMAL, VERBOSE = range(3)

    def __init__(self, level: int = NORMAL, config: pytest.Config | None = None):
        self.level = level
        self.term = TerminalWriter(file=sys.stderr)
        self.suspend_capture = None
        self.resume_capture = None

        if config:
            capman = config.pluginmanager.getplugin('capturemanager')

            if capman:
                self.suspend_capture = getattr(capman, 'suspend_global_capture', getattr('capman', 'suspendcapture', None))
                self.resume_capture = getattr(capman, 'resume_global_capture', getattr('capman', 'resumecapture', None))

    def warning(self, text: str, warner: Callable[..., None] = warnings.warn, suspend: bool = False):
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

        warner(PytestBenchmarkWarning(text))

    def error(self, text: str):
        self.term.line('')
        self.term.sep('-', red=True, bold=True)
        self.term.line(text, red=True, bold=True)
        self.term.sep('-', red=True, bold=True)

    def info(self, text: str, newline: bool = True, **kwargs: bool):
        if self.level >= self.NORMAL:
            if not kwargs or kwargs == {'bold': True}:
                kwargs['purple'] = True

            if newline:
                self.term.line('')

            self.term.line(text, **kwargs)

    def debug(self, text: str, newline: bool = False, **kwargs: bool):
        if self.level >= self.VERBOSE:
            if self.suspend_capture:
                self.suspend_capture(in_=True)

            self.info(text, newline=newline, **kwargs)

            if self.resume_capture:
                self.resume_capture()
