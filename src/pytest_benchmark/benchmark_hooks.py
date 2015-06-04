
def pytest_benchmark_add_extra_info(headerDict):
    """ called during json report preperation.

    Extra information can be added to the report header

    headerDict['user'] = getpass.getuser()

    head_sha = subprocess.check_output('git rev-parse HEAD', shell=True)

    headerDict['revision'] = head_sha.strip()
    """
    pass
