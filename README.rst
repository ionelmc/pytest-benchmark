===============================
pytest-benchmark
===============================

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor|
        | |coveralls| |codecov| |landscape| |scrutinizer|
    * - package
      - |version| |downloads|

..
    |wheel| |supported-versions| |supported-implementations|

.. |docs| image:: https://readthedocs.org/projects/pytest-benchmark/badge/?style=flat
    :target: https://readthedocs.org/projects/pytest-benchmark
    :alt: Documentation Status

.. |travis| image:: http://img.shields.io/travis/ionelmc/pytest-benchmark/master.svg?style=flat&label=Travis
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/pytest-benchmark

.. |appveyor| image:: https://img.shields.io/appveyor/ci/ionelmc/pytest-benchmark/master.svg?style=flat&label=AppVeyor
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/pytest-benchmark

.. |coveralls| image:: http://img.shields.io/coveralls/ionelmc/pytest-benchmark/master.svg?style=flat&label=Coveralls
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/pytest-benchmark

.. |codecov| image:: http://img.shields.io/codecov/c/github/ionelmc/pytest-benchmark/master.svg?style=flat&label=Codecov
    :alt: Coverage Status
    :target: https://codecov.io/github/ionelmc/pytest-benchmark

.. |landscape| image:: https://landscape.io/github/ionelmc/pytest-benchmark/master/landscape.svg?style=flat
    :target: https://landscape.io/github/ionelmc/pytest-benchmark/master
    :alt: Code Quality Status

.. |version| image:: http://img.shields.io/pypi/v/pytest-benchmark.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |downloads| image:: http://img.shields.io/pypi/dm/pytest-benchmark.svg?style=flat
    :alt: PyPI Package monthly downloads
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |wheel| image:: https://pypip.in/wheel/pytest-benchmark/badge.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |supported-versions| image:: https://pypip.in/py_versions/pytest-benchmark/badge.svg?style=flat
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |supported-implementations| image:: https://pypip.in/implementation/pytest-benchmark/badge.svg?style=flat
    :alt: Supported imlementations
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/ionelmc/pytest-benchmark/master.svg?style=flat
    :alt: Scrutinizer Status
    :target: https://scrutinizer-ci.com/g/ionelmc/pytest-benchmark/

A ``py.test`` fixture for benchmarking code. It will group the tests into rounds that are calibrated to the chosen timer. See: calibration_.

* Free software: BSD license

Installation
============

::

    pip install pytest-benchmark

Usage
=====

This plugin provides a `benchmark` fixture. This fixture is a callable object that will benchmark
any function passed to it.

Example:

.. code-block:: python

    def something(duration=0.000001):
        # Code to be measured
        return time.sleep(duration)

    def test_my_stuff(benchmark):
        # benchmark something
        result = benchmark(something)

        # Extra code, to verify that the run completed correctly.
        # Note: this code is not measured.
        assert result is None

You can also pass extra arguments:

.. code-block:: python

    def test_my_stuff(benchmark):
        # benchmark something
        result = benchmark(something, 0.02)

If you need to do some wrapping (like special setup), you can use it as a decorator around a wrapper function:

.. code-block:: python

    def test_my_stuff(benchmark):
        @benchmark
        def result():
            # Code to be measured
            return something(0.0002)

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

Glossary
========

    Iteration
        A single run of your benchmarked function.
    Round
        A set of iterations. The size of a `round` is computed in the calibration phase.

        Stats are computed with rounds, not with iterations. The duration for a round is an average of all the iterations in that round.

        See: calibration_ for an explanation of why it's like this.

Features
========

.. _calibration:

Calibration
-----------

``pytest-benchmark`` will run your function multiple times between measurements. A `round`is that set of runs done between measurements.
This is quite similar to the builtin ``timeit`` module but it's more robust.

The problem with measuring single runs appears when you have very fast code. To illustrate:

.. image:: https://github.com/ionelmc/pytest-benchmark/raw/master/docs/measurement-issues.png
    :alt: Diagram illustrating issues with measuring very fast code

In other words, a `round` is a set of runs that are averaged together, those resulting numbers are then used to compute the result tables.
The default settings will try to keep the round small enough (so that you get to see variance), but not too small, because then you have
the timer calibration issues illustrated above (your test function is faster than or as fast as the resolution of the timer).

Patch utilities
---------------

Suppose you want to benchmark an ``internal`` function from a class:

.. sourcecode:: python

    class Foo(object):
        def __init__(self, arg=0.01):
            self.arg = arg

        def run(self):
            self.internal(self.arg)

        def internal(self, duration):
            time.sleep(duration)

With the ``benchmark`` fixture this is quite hard to test if you don't control the ``Foo`` code or it has very
complicated construction.

For this there's an experimental ``benchmark_weave`` fixture that can patch stuff using `aspectlib
<https://github.com/ionelmc/python-aspectlib>`_ (make sure you `pip install apectlib` or `pip install
pytest-benchmark[aspect]`):

.. sourcecode:: python

    def test_foo(benchmark_weave):
        with benchmark_weave(Foo.internal, lazy=True):
            f = Foo()
            f.run()

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
