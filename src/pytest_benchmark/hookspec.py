"""
..
  PYTEST_DONT_REWRITE
"""

from typing import Any

import pytest

from .fixture import BenchmarkFixture
from .session import BenchmarkSession


@pytest.hookspec(firstresult=True)
def pytest_benchmark_scale_unit(
    config: pytest.Config,
    unit,
    benchmarks: BenchmarkFixture,
    best,
    worst,
    sort,
) -> None:
    """
    To have custom time scaling do something like this:

    .. sourcecode:: python

        def pytest_benchmark_scale_unit(config, unit, benchmarks, best, worst, sort):
            if unit == 'seconds':
                prefix = ''
                scale = 1.0
            elif unit == 'operations':
                prefix = 'K'
                scale = 0.001
            else:
                raise RuntimeError("Unexpected measurement unit %r" % unit)

            return prefix, scale
    """


@pytest.hookspec(firstresult=True)
def pytest_benchmark_generate_machine_info(
    config: pytest.Config,
) -> None:
    """
    To completely replace the generated machine_info do something like this:

    .. sourcecode:: python

        def pytest_benchmark_generate_machine_info(config):
            return {'user': getpass.getuser()}
    """


def pytest_benchmark_update_machine_info(
    config: pytest.Config,
    machine_info: dict[str, Any],
) -> None:
    """
    If benchmarks are compared and machine_info is different, warnings will be shown.

    To add the current user to the commit info override the hook in your conftest.py like this:

    .. sourcecode:: python

        def pytest_benchmark_update_machine_info(config, machine_info):
            machine_info['user'] = getpass.getuser()
    """


@pytest.hookspec(firstresult=True)
def pytest_benchmark_generate_commit_info(
    config: pytest.Config,
) -> None:
    """
    To completely replace the generated commit_info do something like this:

    .. sourcecode:: python

        def pytest_benchmark_generate_commit_info(config):
            return {'id': subprocess.check_output(['svnversion']).strip()}
    """


def pytest_benchmark_update_commit_info(
    config: pytest.Config,
    commit_info: dict[str, Any],
) -> None:
    """
    To add something into the commit_info, like the commit message do something like this:

    .. sourcecode:: python

        def pytest_benchmark_update_commit_info(config, commit_info):
            commit_info['message'] = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).strip()
    """


@pytest.hookspec(firstresult=True)
def pytest_benchmark_group_stats(
    config: pytest.Config,
    benchmarks: BenchmarkFixture,
    group_by: str,
) -> None:
    """
    You may perform grouping customization here, in case the builtin grouping doesn't suit you.

    Example:

    .. sourcecode:: python

        @pytest.hookimpl(wrapper=True)
        def pytest_benchmark_group_stats(config, benchmarks, group_by):
            outcome = yield
            if group_by == "special":  # when you use --benchmark-group-by=special
                result = defaultdict(list)
                for bench in benchmarks:
                    # `bench.special` doesn't exist, replace with whatever you need
                    result[bench.special].append(bench)
                outcome.force_result(result.items())
    """


@pytest.hookspec(firstresult=True)
def pytest_benchmark_generate_json(
    config: pytest.Config,
    benchmarks: list[BenchmarkFixture],
    include_data,
    machine_info: dict[str, Any],
    commit_info: dict[str, Any],
) -> None:
    """
    You should read pytest-benchmark's code if you really need to wholly customize the JSON.

    .. warning::

        Improperly customizing this may cause breakage if ``--benchmark-compare`` or ``--benchmark-histogram`` are used.

    By default, ``pytest_benchmark_generate_json`` strips benchmarks that have errors from the output. To prevent this,
    implement the hook like this:

    .. sourcecode:: python

        @pytest.hookimpl(wrapper=True)
        def pytest_benchmark_generate_json(config, benchmarks, include_data, machine_info, commit_info):
            for bench in benchmarks:
                bench.has_error = False
            yield
    """


def pytest_benchmark_update_json(
    config: pytest.Config,
    benchmarks: list[BenchmarkFixture],
    output_json: Any,
) -> None:
    """
    Use this to add custom fields in the output JSON.

    Example:

    .. sourcecode:: python

        def pytest_benchmark_update_json(config, benchmarks, output_json):
            output_json['foo'] = 'bar'
    """


def pytest_benchmark_compare_machine_info(
    config: pytest.Config,
    benchmarksession: BenchmarkSession,
    machine_info: str,
    compared_benchmark: BenchmarkFixture,
) -> None:
    """
    You may want to use this hook to implement custom checks or abort execution.
    ``pytest-benchmark`` builtin hook does this:

    .. sourcecode:: python

        def pytest_benchmark_compare_machine_info(config, benchmarksession, machine_info, compared_benchmark):
            if compared_benchmark["machine_info"] != machine_info:
                benchmarksession.logger.warning(
                    "Benchmark machine_info is different. Current: %s VS saved: %s." % (
                        format_dict(machine_info),
                        format_dict(compared_benchmark["machine_info"]),
                    )
            )
    """
