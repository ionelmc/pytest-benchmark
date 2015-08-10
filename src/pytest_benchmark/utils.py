from __future__ import division
from __future__ import print_function

import argparse
import os
import subprocess
import sys
import types
from datetime import datetime
from decimal import Decimal

from .compat import PY3

try:
    from subprocess import check_output
except ImportError:
    def check_output(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output


class SecondsDecimal(Decimal):
    def __float__(self):
        return float(super(SecondsDecimal, self).__str__())

    def __str__(self):
        return "{0}s".format(time_format(float(super(SecondsDecimal, self).__str__())))

    @property
    def as_string(self):
        return super(SecondsDecimal, self).__str__()


class NameWrapper(object):
    def __init__(self, target):
        self.target = target

    def __str__(self):
        name = self.target.__module__ + "." if hasattr(self.target, '__module__') else ""
        name += self.target.__name__ if hasattr(self.target, '__name__') else repr(self.target)
        return name

    def __repr__(self):
        return "NameWrapper(%s)" % repr(self.target)


def get_commit_id():
    info = get_commit_info()
    return '%s_%s%s' % (info['id'], get_current_time(), '_uncommitted-changes' if info['dirty'] else '')


def get_commit_info():
    dirty = False
    commit = 'unversioned'
    if os.path.exists('.git'):
        desc = check_output('git describe --dirty --always --long --abbrev=40'.split(),
                            universal_newlines=True).strip()
        desc = desc.split('-')
        if desc[-1].strip() == 'dirty':
            dirty = True
            desc.pop()
        commit = desc[-1].strip('g')
    elif os.path.exists('.hg'):
        desc = check_output('hg id --id --debug'.split(), universal_newlines=True).strip()
        if desc[-1] == '+':
            dirty = True
        commit = desc.strip('+')
    return {
        'id': commit,
        'dirty': dirty
    }


def get_current_time():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def first_or_false(obj):
    if obj:
        value, = obj
    else:
        value = False

    return value


def load_timer(string):
    if "." not in string:
        raise argparse.ArgumentTypeError("Value for --benchmark-timer must be in dotted form. Eg: 'module.attr'.")
    mod, attr = string.rsplit(".", 1)
    if mod == 'pep418':
        if PY3:
            import time
            return NameWrapper(getattr(time, attr))
        else:
            from . import pep418
            return NameWrapper(getattr(pep418, attr))
    else:
        __import__(mod)
        mod = sys.modules[mod]
        return NameWrapper(getattr(mod, attr))


def parse_timer(string):
    return str(load_timer(string))


def parse_sort(string):
    if string not in ("min", "max", "mean", "stddev"):
        raise argparse.ArgumentTypeError("Value for --benchmark-sort must be one of: 'min', 'max', 'mean' or 'stddev'.")
    return string


def parse_rounds(string):
    try:
        value = int(string)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(exc)
    else:
        if value < 1:
            raise argparse.ArgumentTypeError("Value for --benchmark-rounds must be at least 1.")
        return value


def parse_seconds(string):
    try:
        return SecondsDecimal(string).as_string
    except Exception as exc:
        raise argparse.ArgumentTypeError("Invalid decimal value %r: %r" % (string, exc))


def parse_save(string):
    if not string:
        raise argparse.ArgumentTypeError("Can't be empty.")
    if any(c in string for c in r"\/:*?<>|"):
        raise argparse.ArgumentTypeError("Must not contain any of these characters: /:*?<>|\\")
    return string


def time_unit(value):
    if value < 1e-6:
        return "n", 1e9
    elif value < 1e-3:
        return "u", 1e6
    elif value < 1:
        return "m", 1e3
    else:
        return "", 1.


def time_format(value):
    unit, adjustment = time_unit(value)
    return "{0:.2f}{1:s}".format(value * adjustment, unit)


class cached_property(object):
    def __init__(self, func):
        self.__doc__ = getattr(func, '__doc__')
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def clonefunc(f):
    """Deep clone the given function to create a new one.

    By default, the PyPy JIT specializes the assembler based on f.__code__:
    clonefunc makes sure that you will get a new function with a **different**
    __code__, so that PyPy will produce independent assembler. This is useful
    e.g. for benchmarks and microbenchmarks, so you can make sure to compare
    apples to apples.

    Use it with caution: if abused, this might easily produce an explosion of
    produced assembler.

    from: https://bitbucket.org/antocuni/pypytools/src/tip/pypytools/util.py?at=default
    """

    # first of all, we clone the code object
    try:
        co = f.__code__
        co2 = types.CodeType(co.co_argcount, co.co_nlocals, co.co_stacksize, co.co_flags, co.co_code,
                             co.co_consts, co.co_names, co.co_varnames, co.co_filename, co.co_name,
                             co.co_firstlineno, co.co_lnotab, co.co_freevars, co.co_cellvars)
        #
        # then, we clone the function itself, using the new co2
        return types.FunctionType(co2, f.__globals__, f.__name__, f.__defaults__, f.__closure__)
    except AttributeError:
        return f
