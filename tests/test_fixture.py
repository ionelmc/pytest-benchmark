import time
from types import SimpleNamespace

from pytest_benchmark.fixture import BenchmarkFixture
from pytest_benchmark.utils import NameWrapper


def test_fullname_uses_public_nodeid():
    # pytest main removed the private ``_nodeid`` (structured NodeId change),
    # the public ``nodeid`` string is the supported contract.
    node = SimpleNamespace(name='test_example', nodeid='test_example.py::test_example')
    assert not hasattr(node, '_nodeid')

    fixture = BenchmarkFixture(
        node,
        disable_gc=False,
        timer=NameWrapper(time.perf_counter),
        min_rounds=5,
        min_time=0.000005,
        max_time=1.0,
        precision=None,
        confidence=None,
        warmup=False,
        warmup_iterations=100000,
        calibration_precision=10,
        add_stats=[].append,
        logger=None,
        warner=None,
        disabled=False,
        cprofile=None,
        cprofile_loops=1,
        cprofile_dump=False,
    )

    assert fixture.name == 'test_example'
    assert fixture.fullname == 'test_example.py::test_example'
