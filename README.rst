===============================
pytest-benchmark
===============================

.. image:: http://img.shields.io/travis/ionelmc/pytest-benchmark/master.png
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/pytest-benchmark

.. image:: https://ci.appveyor.com/api/projects/status/ojmf55r6usb1ih5e/branch/master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/pytest-benchmark

.. image:: http://img.shields.io/coveralls/ionelmc/pytest-benchmark/master.png
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/pytest-benchmark

.. image:: http://img.shields.io/pypi/v/pytest-benchmark.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pytest-benchmark

.. image:: http://img.shields.io/pypi/dm/pytest-benchmark.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/pytest-benchmark

py.test fixture for benchmarking code

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
