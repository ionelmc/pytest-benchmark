
Changelog
=========

3.0.0a4 (2015-10-08)
--------------------

* Changed how failures to get commit info are handled: now they are soft failures. Previously it made the whole
  test suite fail, just because you didn't have ``git/hg`` installed.

3.0.0a3 (2015-10-02)
--------------------

* Added progress indication when computing stats.

3.0.0a2 (2015-09-30)
--------------------

* Fixed accidental output capturing caused by capturemanager misuse.

3.0.0a1 (2015-09-13)
--------------------

* Added JSON report saving (the ``--benchmark-json`` command line arguments).
* Added benchmark data storage(the ``--benchmark-save`` and ``--benchmark-autosave`` command line arguments).
* Added comparison to previous runs (the ``--benchmark-compare`` command line argument).
* Added performance regression checks (the ``--benchmark-compare-fail`` command line argument).
* Added possibility to group by various parts of test name (the `--benchmark-compare-group-by`` command line argument).
* Added historical plotting (the ``--benchmark-histogram`` command line argument).
* Added option to fine tune the calibration (the ``--benchmark-calibration-precision`` command line argument and
  ``calibration_precision`` marker option).

* Changed ``benchmark_weave`` to no longer be a context manager. Cleanup is performed automatically. *BACKWARDS INCOMPATIBLE*
* Added ``benchmark.weave`` method (alternative to ``benchmark_weave`` fixture).

* Added new hooks to allow customization:

  * ``pytest_benchmark_generate_machine_info(config)``
  * ``pytest_benchmark_update_machine_info(config, info)``
  * ``pytest_benchmark_generate_commit_info(config)``
  * ``pytest_benchmark_update_commit_info(config, info)``
  * ``pytest_benchmark_group_stats(config, benchmarks, group_by)``
  * ``pytest_benchmark_generate_json(config, benchmarks, include_data)``
  * ``pytest_benchmark_update_json(config, benchmarks, output_json)``
  * ``pytest_benchmark_compare_machine_info(config, benchmarksession, machine_info, compared_benchmark)``

* Changed the timing code to:

  * Tracers are automatically disabled when running the test function (like coverage tracers).
  * Fixed an issue with calibration code getting stuck.

* Added `pedantic mode` via ``benchmark.pedantic()``. This mode disables calibration and allows a setup function.


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

* Replace the context-manager based API with a simple callback interface. *BACKWARDS INCOMPATIBLE*
* Implement timer calibration for precise measurements.

1.0.0 (2014-12-15)
------------------

* Use a precise default timer for PyPy.

? (?)
-----

* Readme and styling fixes (contributed by Marc Abramowitz)
* Lots of wild changes.
