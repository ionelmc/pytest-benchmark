from __future__ import division
from __future__ import print_function

import sys

import py


class Logger(object):
    def __init__(self, verbose, config=None):
        self.verbose = verbose
        self.term = py.io.TerminalWriter(file=sys.stderr)
        if config:
            self.capman = config.pluginmanager.getplugin("capturemanager")
            self.pytest_warn = config.warn
        else:
            self.capman = None
            self.pytest_warn = lambda **kwargs: None
        try:
            self.pytest_warn_has_fslocation = 'fslocation' in config.warn.func_code.co_varnames
        except AttributeError:
            self.pytest_warn_has_fslocation = False

    def warn(self, code, text, warner=None, suspend=False, fslocation=None):
        if self.verbose:
            if suspend and self.capman:
                self.capman.suspendcapture(in_=True)
            self.term.line("")
            self.term.sep("-", red=True, bold=True)
            self.term.write(" WARNING: ", red=True, bold=True)
            self.term.line(text, red=True)
            self.term.sep("-", red=True, bold=True)
            if suspend and self.capman:
                self.capman.resumecapture()
        if warner is None:
            warner = self.pytest_warn
        if fslocation and self.pytest_warn_has_fslocation:
            warner(code=code, message=text, fslocation=fslocation)
        else:
            warner(code=code, message=text)

    def error(self, text):
        self.term.line("")
        self.term.sep("-", red=True, bold=True)
        self.term.line(text, red=True, bold=True)
        self.term.sep("-", red=True, bold=True)

    def info(self, text, newline=True, **kwargs):
        if not kwargs or kwargs == {'bold': True}:
            kwargs['purple'] = True
        if newline:
            self.term.line("")
        self.term.line(text, **kwargs)

    def debug(self, text, **kwargs):
        if self.verbose:
            if self.capman:
                self.capman.suspendcapture(in_=True)
            self.info(text, **kwargs)
            if self.capman:
                self.capman.resumecapture()
