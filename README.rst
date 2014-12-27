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

.. code-block:: python

    def test_my_stuff(benchmark):
        @benchmark
        def result():
            # Code to be measured
            return time.sleep(0.000001)

        # Extra code, to verify that the run completed correctly.
        # Note: this code is not measured.
        assert result is None

``py.test`` command-line options:

    --benchmark-min-time=BENCHMARK_MIN_TIME
                          Minimum time per round. Default: 25.00us
    --benchmark-max-time=BENCHMARK_MAX_TIME
                          Maximum time to spend in a benchmark. Default: 1.00s
    --benchmark-min-rounds=BENCHMARK_MIN_ROUNDS
                          Minimum rounds, even if total time would exceed `--max-time`. Default: 5
    --benchmark-sort=BENCHMARK_SORT
                          Column to sort on. Can be one of: 'min', 'max', 'mean' or 'stddev'.
                          Default: min
    --benchmark-timer=BENCHMARK_TIMER
                          Timer to use when measuring time. Default: time.perf_counter
    --benchmark-warmup    Runs the benchmarks two times. Discards data from the first run.
    --benchmark-warmup-iterations=BENCHMARK_WARMUP_ITERATIONS
                          Max number of iterations to run in the warmup phase. Default: 100000
    --benchmark-verbose   Dump diagnostic and progress information.
    --benchmark-disable-gc
                          Disable GC during benchmarks.
    --benchmark-skip      Skip running any benchmarks.
    --benchmark-only      Only run benchmarks.


Setting per-test options:

.. code-block:: python

    @pytest.mark.benchmark(
        group="group-name",
        min_time=0.1,
        max_time=0.5,
        min_rounds=5,
        timer=time.time,
        disable_gc=True,
        warmup=False
    )
    def test_my_stuff(benchmark):
        @benchmark
        def result():
            # Code to be measured
            return time.sleep(0.000001)

        # Extra code, to verify that the run
        # completed correctly.
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

Credits
=======

* Timing code and ideas taken from: https://bitbucket.org/haypo/misc/src/tip/python/benchmark.py
