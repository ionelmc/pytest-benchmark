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

Documentation
=============

`pytest-benchmark.readthedocs.org <http://pytest-benchmark.readthedocs.org/en/stable/>`_

Examples
========

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
        result = benchmark(time.sleep, 0.02)


Screenshots
-----------

Normal run:

.. image:: https://github.com/ionelmc/pytest-benchmark/raw/master/docs/screenshot.png
    :alt: Screenshot of py.test summary

Compare mode (``--benchmark-compare``):

.. image:: https://github.com/ionelmc/pytest-benchmark/raw/master/docs/screenshot-compare.png
    :alt: Screenshot of py.test summary in compare mode

Histogram (``--benchmark-histogram``):

.. image:: https://cdn.rawgit.com/ionelmc/pytest-benchmark/94860cc8f47aed7ba4f9c7e1380c2195342613f6/docs/sample-tests_test_normal.py_test_xfast_parametrized%5B0%5D.svg
    :alt: Histogram sample

..

    Also, it has `nice tooltips
    <https://cdn.rawgit.com/ionelmc/pytest-benchmark/94860cc8f47aed7ba4f9c7e1380c2195342613f6/docs/sample-tests_test_normal.py_test_xfast_parametrized%5B0%5D.svg>`_.

Development
===========

To run the all tests run::

    tox

Credits
=======

* Timing code and ideas taken from: https://bitbucket.org/haypo/misc/src/tip/python/benchmark.py

.. _FAQ: http://pytest-benchmark.readthedocs.org/en/stable/faq.html
.. _calibration: http://pytest-benchmark.readthedocs.org/en/stable/features.html#calibration





