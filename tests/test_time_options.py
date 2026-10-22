import argparse
from decimal import Decimal

import pytest

from pytest_benchmark.utils import parse_seconds

pytest_plugins = ('pytester',)


@pytest.mark.parametrize('value', ['NaN', 'sNaN', 'Infinity', '-Infinity', '-1'])
def test_seconds_reject_invalid_durations(value):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_seconds(value)


@pytest.mark.parametrize('value', ['0', '0.000005', '1', '1e-6'])
def test_seconds_accept_finite_nonnegative_durations(value):
    assert Decimal(parse_seconds(value)) == Decimal(value)


@pytest.mark.parametrize('option', ['--benchmark-min-time', '--benchmark-max-time'])
@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-1'])
def test_invalid_time_is_a_usage_error(pytester, option, value):
    pytester.makepyfile('def test_example(benchmark): benchmark(lambda: None)')
    result = pytester.runpytest(f'{option}={value}')
    assert result.ret == pytest.ExitCode.USAGE_ERROR
    assert 'Invalid decimal value' in result.stderr.str()
