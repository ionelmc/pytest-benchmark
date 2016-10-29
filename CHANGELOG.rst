
Changelog
=========

3.1.0a1 (2016-10-29)
--------------------

* Added ``--benchmark-colums`` command line option. It selects what columns are displayed in the result table. Contributed by
  Antonio Cuni in `#34 <https://github.com/ionelmc/pytest-benchmark/pull/34>`_.
* Added support for grouping by specific test parametrization (``--benchmark-group-by=param:NAME`` where ``NAME`` is your
  param name). Contributed by Antonio Cuni in `#37 <https://github.com/ionelmc/pytest-benchmark/pull/37>`_.
* Added support for `name` or `fullname` in ``--benchmark-sort``.
  Contributed by Antonio Cuni in `#37 <https://github.com/ionelmc/pytest-benchmark/pull/37>`_.
* Changed signature for ``pytest_benchmark_generate_json`` hook to take 2 new arguments: ``machine_info`` and ``commit_info``.
* Changed `--benchmark-histogram`` to plot groups instead of name-matching runs.
* Changed `--benchmark-histogram`` to plot exactly what you compared against. Now it's ``1:1`` with the compare feature.
* Changed `--benchmark-compare`` to allow globs. You can compare against all the previous runs now.
* Changed `--benchmark-group-by`` to allow multiple values separated by comma.
  Example: ``--benchmark-group-by=param:foo,param:bar``
* Added a command line tool to compare previous data: ``py.test-benchmark``. It has two commands:

  * ``list`` - Lists all the available files.
  * ``compare`` - Displays result tables. Takes optional arguments:

    * ``--sort=COL``
    * ``--group-by=LABEL``
    * ``--columns=LABELS``
    * ``--histogram=[FILENAME-PREFIX]``
* Added ``--benchmark-cprofile`` that profiles last run of benchmarked function.  Contributed by Petr Šebek.
* Changed ``--benchmark-storage`` so it now allows elasticsearch storage. It allows to store data to elasticsearch instead to
  json files. Contributed by Petr Šebek in `#58 <https://github.com/ionelmc/pytest-benchmark/pull/58>`_.

3.0.0 (2015-11-08)
------------------

* Improved ``--help`` text for ``--benchmark-histogram``, ``--benchmark-save`` and ``--benchmark-autosave``.
* Benchmarks that raised exceptions during test now have special highlighting in result table (red background).
* Benchmarks that raised exceptions are not included in the saved data anymore (you can still get the old behavior back
  by implementing ``pytest_benchmark_generate_json`` in your ``conftest.py``).
* The plugin will use pytest's warning system for warnings. There are 2 categories: ``WBENCHMARK-C`` (compare mode
  issues) and ``WBENCHMARK-U`` (usage issues).
* The red warnings are only shown if ``--benchmark-verbose`` is used. They still will be always be shown in the
  pytest-warnings section.
* Using the benchmark fixture more than one time is disallowed (will raise exception).
* Not using the benchmark fixture (but requiring it) will issue a warning (``WBENCHMARK-U1``).

3.0.0rc1 (2015-10-25)
---------------------

* Changed ``--benchmark-warmup`` to take optional value and automatically activate on PyPy (default value is ``auto``).
  **MAY BE BACKWARDS INCOMPATIBLE**
* Removed the version check in compare mode (previously there was a warning if current version is lower than what's in
  the file).

3.0.0b3 (2015-10-22)
---------------------

* Changed how comparison is displayed in the result table. Now previous runs are shown as normal runs and names get a
  special suffix indicating the origin. Eg: "test_foobar (NOW)" or "test_foobar (0123)".
* Fixed sorting in the result table. Now rows are sorted by the sort column, and then by name.
* Show the plugin version in the header section.
* Moved the display of default options in the header section.

3.0.0b2 (2015-10-17)
---------------------

* Add a ``--benchmark-disable`` option. It's automatically activated when xdist is on
* When xdist is on or `statistics` can't be imported then ``--benchmark-disable`` is automatically activated (instead
  of ``--benchmark-skip``). **BACKWARDS INCOMPATIBLE**
* Replace the deprecated ``__multicall__`` with the new hookwrapper system.
* Improved description for ``--benchmark-max-time``.

3.0.0b1 (2015-10-13)
--------------------

* Tests are sorted alphabetically in the results table.
* Failing to import `statistics` doesn't create hard failures anymore. Benchmarks are automatically skipped if import
  failure occurs. This would happen on Python 3.2 (or earlier Python 3).

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

* Added JSON report saving (the ``--benchmark-json`` command line arguments). Based on initial work from Dave Collins in
  `#8 <https://github.com/ionelmc/pytest-benchmark/pull/8>`_.
* Added benchmark data storage(the ``--benchmark-save`` and ``--benchmark-autosave`` command line arguments).
* Added comparison to previous runs (the ``--benchmark-compare`` command line argument).
* Added performance regression checks (the ``--benchmark-compare-fail`` command line argument).
* Added possibility to group by various parts of test name (the `--benchmark-compare-group-by`` command line argument).
* Added historical plotting (the ``--benchmark-histogram`` command line argument).
* Added option to fine tune the calibration (the ``--benchmark-calibration-precision`` command line argument and
  ``calibration_precision`` marker option).

* Changed ``benchmark_weave`` to no longer be a context manager. Cleanup is performed automatically.
  **BACKWARDS INCOMPATIBLE**
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

* Replace the context-manager based API with a simple callback interface. **BACKWARDS INCOMPATIBLE**
* Implement timer calibration for precise measurements.

1.0.0 (2014-12-15)
------------------

* Use a precise default timer for PyPy.

? (?)
-----

* Readme and styling fixes. Contributed by Marc Abramowitz in `#4 <https://github.com/ionelmc/pytest-benchmark/pull/4>`_.
* Lots of wild changes.
