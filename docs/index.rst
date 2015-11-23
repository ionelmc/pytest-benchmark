Welcome to pytest-benchmark's documentation!
============================================

This plugin provides a `benchmark` fixture. This fixture is a callable object that will benchmark any function passed
to it.

Notable features and goals:

* Sensible defaults and automatic calibration for microbenchmarks
* Good integration with pytest
* Comparison and regression tracking
* Exhausive statistics
* JSON export

Examples:

.. code-block:: python

    def something(duration=0.000001):
        """
        Function that needs some serious benchmarking.
        """
        time.sleep(duration)
        # You may return anything you want, like the result of a computation
        return 123

    def test_my_stuff(benchmark):
        # benchmark something
        result = benchmark(something)

        # Extra code, to verify that the run completed correctly.
        # Sometimes you may want to check the result, fast functions
        # are no good if they return incorrect results :-)
        assert result == 123

    def test_my_stuff_different_arg(benchmark):
        # benchmark something, but add some arguments
        result = benchmark(something, 0.001)
        assert result == 123

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

    Also, it has `nice tooltips <https://cdn.rawgit.com/ionelmc/pytest-benchmark/master/docs/sample.svg>`_.

User guide
==========

.. toctree::
   :maxdepth: 2

   installation

   usage
   calibration
   pedantic
   comparing

   hooks
   faq
   glossary
   contributing
   authors
   changelog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

