
Changelog
=========

2.5.0 (2015-06-20)
------------------

* Improved test suite a bit (not using `cram` anymore).
* Improved help text on the ``--benchmark-warmup`` option.
* Made ``warmup_iterations`` available as a marker argument (eg: ``@pytest.mark.benchmark(warmup_iterations=1234)``).
* Fixed ``--benchmark-verbose``'s printouts to work properly with output capturing.
* Changed how warmup iterations are computed (now number of total iterations is used, instead of just the rounds).
* Fixed a bug where calibration would run forever.
* Disabled red/green coloring (it was kinda random) when there's a single test in the results table.

2.4.1 (2015-03-16)
------------------

* Fix regression, plugin was raising ``ValueError: no option named 'dist'`` when xdist wasn't installed.

2.4.0 (2015-03-12)
------------------

* Add a ``benchmark_weave`` experimental fixture.
* Fix internal failures when `xdist` plugin is active.
* Automatically disable benchmarks if `xdist` is active.

2.3.0 (2014-12-27)
------------------

* Moved the warmup in the calibration phase. Solves issues with benchmarking on PyPy.

  Added a ``--benchmark-warmup-iterations`` option to fine-tune that.

2.2.0 (2014-12-26)
------------------

* Make the default rounds smaller (so that variance is more accurate).
* Show the defaults in the ``--help`` section.

2.1.0 (2014-12-20)
------------------

* Simplify the calibration code so that the round is smaller.
* Add diagnostic output for calibration code (``--benchmark-verbose``).

2.0.0 (2014-12-19)
------------------

* Replace the context-manager based API with a simple callback interface.
* Implement timer calibration for precise measurements.

1.0.0 (2014-12-15)
------------------

* Use a precise default timer for PyPy.

? (?)
-----

* Readme and styling fixes (contributed by Marc Abramowitz)
* Lots of wild changes.
