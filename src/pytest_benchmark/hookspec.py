def pytest_benchmark_machine_info(info):
    """
    Called during JSON report preparation. Must return a dictionary or ``info``.

    If benchmarks are compared and machine_info is different then warnings will be shown.

    To add the current user to the commit info override the hook in your conftest.py like this:

    .. sourcecode:: python

        def pytest_benchmark_update_machine_info(info):
            info['user'] = getpass.getuser()
            return info

    Or to completely replace the dict:

    .. sourcecode:: python

        def pytest_benchmark_update_machine_info():
            return {'user': getpass.getuser()}
    """
    pass


def pytest_benchmark_group_stats(config, benchmarks, group_by):
    pass


def pytest_benchmark_generate_json(config, machine_info, commit_info, benchmarks):
    pass
