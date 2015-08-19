=====
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


Commandline options
===================

``py.test`` command-line options:

  --benchmark-min-time=SECONDS
                        Minimum time per round in seconds. Default: '0.000025'
  --benchmark-max-time=SECONDS
                        Maximum time to spend in a benchmark in seconds.
                        Default: '1.0'
  --benchmark-min-rounds=NUM
                        Minimum rounds, even if total time would exceed
                        `--max-time`. Default: 5
  --benchmark-sort=COL  Column to sort on. Can be one of: 'min', 'max', 'mean'
                        or 'stddev'. Default: 'min'
  --benchmark-group-by=LABEL
                        How to group tests. Can be one of: 'group', 'name',
                        'fullname', 'func', 'fullfunc' or 'param'. Default:
                        'group'
  --benchmark-timer=FUNC
                        Timer to use when measuring time. Default: 'time.time'
  --benchmark-warmup    Activates warmup. Will run the test function up to
                        number of times in the calibration phase. See
                        `--benchmark-warmup-iterations`. Note: Even the warmup
                        phase obeys --benchmark-max-time.
  --benchmark-warmup-iterations=NUM
                        Max number of iterations to run in the warmup phase.
                        Default: 100000
  --benchmark-verbose   Dump diagnostic and progress information.
  --benchmark-disable-gc
                        Disable GC during benchmarks.
  --benchmark-skip      Skip running any benchmarks.
  --benchmark-only      Only run benchmarks.
  --benchmark-save=NAME
                        Save the current run into 'STORAGE-PATH/counter-
                        NAME.json'. Default: 'e689af57e7439b9005749d806248897a
                        d550eab5_20150811_041632_uncommitted-changes'
  --benchmark-autosave  Autosave the current run into 'STORAGE-PATH/counter-
                        commit_id.json
  --benchmark-save-data
                        Use this to make --benchmark-save and --benchmark-
                        autosave include all the timing data, not just the
                        stats.
  --benchmark-compare=NUM
                        Compare the current run against run NUM or the latest
                        saved run if unspecified.
  --benchmark-compare-fail=EXPR
                        Fail test if performance regresses according to given
                        EXPR (eg: min:5% or mean:0.001 for number of seconds).
                        Can be used multiple times.
  --benchmark-storage=STORAGE-PATH
                        Specify a different path to store the runs (when
                        --benchmark-save or --benchmark-autosave are used).
                        Default: './.benchmarks/Linux-CPython-2.7-64bit'
  --benchmark-histogram=FILENAME-PREFIX
                        Plot graphs of min/max/avg/stddev over time in
                        FILENAME-PREFIX-test_name.svg. Default:
                        'benchmark_20150811_041632'
  --benchmark-json=PATH
                        Dump a JSON report into PATH. Note that this will
                        include the complete data (all the timings, not just
                        the stats).

Markers
=======

You can set per-test options with the ``benchmark`` marker:

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
