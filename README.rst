===============================
pytest-benchmark
===============================

| |docs| |travis| |appveyor| |coveralls| |landscape| |scrutinizer|
| |version| |downloads| |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/pytest-benchmark/badge/?style=flat
    :target: https://readthedocs.org/projects/pytest-benchmark
    :alt: Documentation Status

.. |travis| image:: http://img.shields.io/travis/ionelmc/pytest-benchmark/master.png?style=flat
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/pytest-benchmark

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/ionelmc/pytest-benchmark?branch=master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/pytest-benchmark

.. |coveralls| image:: http://img.shields.io/coveralls/ionelmc/pytest-benchmark/master.png?style=flat
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/pytest-benchmark

.. |landscape| image:: https://landscape.io/github/ionelmc/pytest-benchmark/master/landscape.svg?style=flat
    :target: https://landscape.io/github/ionelmc/pytest-benchmark/master
    :alt: Code Quality Status

.. |version| image:: http://img.shields.io/pypi/v/pytest-benchmark.png?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-benchmark.png?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |wheel| image:: https://pypip.in/wheel/pytest-benchmark/badge.png?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |supported-versions| image:: https://pypip.in/py_versions/pytest-benchmark/badge.png?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |supported-implementations| image:: https://pypip.in/implementation/pytest-benchmark/badge.png?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/ionelmc/pytest-benchmark/master.png?style=flat
    :alt: Scrtinizer Status
    :target: https://scrutinizer-ci.com/g/ionelmc/pytest-benchmark/

A ``py.test`` fixture for benchmarking code.

* Free software: BSD license

Installation
============

::

    pip install pytest-benchmark

Usage
=====

::

    def test_my_stuff(benchmark):
        with benchmark:
            # Code to be measured
            result = time.sleep(0.000001)

        # Extra code, to verify that the run completed correctly.
        # Note: this code is not measured.
        assert result is None

``py.test`` command-line options:

  benchmark:
    --benchmark-max-time=BENCHMARK_MAX_TIME
                          Maximum time to spend in a benchmark (including
                          overhead).
    --benchmark-max-iterations=BENCHMARK_MAX_ITERATIONS
                          Maximum iterations to do.
    --benchmark-min-iterations=BENCHMARK_MIN_ITERATIONS
                          Minium iterations, even if total time would exceed
                          `max-time`.
    --benchmark-timer=BENCHMARK_TIMER
                          Timer to use when measuring time.
    --benchmark-disable-gc
                          Disable GC during benchmarks.
    --benchmark-skip      Skip running any benchmarks.
    --benchmark-only      Only run benchmarks.

Setting per-test options::

::

    @pytest.mark.benchmark(group="group-name", max_time=0.5, max_iterations=5000, min_iterations=5, timer=time.time, disable_gc=True)
    def test_my_stuff(benchmark):
        with benchmark:
            # Code to be measured
            result = time.sleep(0.000001)

        # Extra code, to verify that the run completed correctly.
        # Note: this code is not measured.
        assert result is None


Documentation
=============

https://pytest-benchmark.readthedocs.org/

Obligatory screenshot
=====================

.. image:: https://github.com/ionelmc/pytest-benchmark/raw/master/docs/screenshot.png
    :alt: Screenshot of py.test summary

Development
===========

To run the all tests run::

    tox
