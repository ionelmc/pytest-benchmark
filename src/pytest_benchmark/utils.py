from __future__ import division
from __future__ import print_function

from decimal import Decimal
import argparse
import sys
import os
import subprocess
from datetime import datetime

from .compat import PY3


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
        desc = subprocess.check_output('git describe --dirty --always --long --abbrev=40'.split()).strip()
        desc = desc.split('-')
        if desc[-1].strip() == 'dirty':
            dirty = True
            desc.pop()
        commit = desc[-1].strip('g')
    elif os.path.exists('.hg'):
        desc = subprocess.check_output('hg id --id --debug'.split()).strip()
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

