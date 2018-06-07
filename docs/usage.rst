=====
Usage
=====

This plugin provides a `benchmark` fixture. This fixture is a callable object that will benchmark any function passed
to it.

Example:

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

You can also pass extra arguments:

.. code-block:: python

    def test_my_stuff(benchmark):
        benchmark(time.sleep, 0.02)

Or even keyword arguments:

.. code-block:: python

    def test_my_stuff(benchmark):
        benchmark(time.sleep, duration=0.02)

Another pattern seen in the wild, that is not recommended for micro-benchmarks (very fast code) but may be convenient:

.. code-block:: python

    def test_my_stuff(benchmark):
        @benchmark
        def something():  # unnecessary function call
            time.sleep(0.000001)

A better way is to just benchmark the final function:

.. code-block:: python

    def test_my_stuff(benchmark):
        benchmark(time.sleep, 0.000001)  # way more accurate results!

If you need to do fine control over how the benchmark is run (like a `setup` function, exact control of `iterations` and
`rounds`) there's a special mode - pedantic_:

.. code-block:: python

    def my_special_setup():
        ...

    def test_with_setup(benchmark):
        benchmark.pedantic(something, setup=my_special_setup, args=(1, 2, 3), kwargs={'foo': 'bar'}, iterations=10, rounds=100)

Commandline options
===================

``py.test`` command-line options:

  --benchmark-min-time=SECONDS
                        Minimum time per round in seconds. Default: '0.000005'
  --benchmark-max-time=SECONDS
                        Maximum run time per test - it will be repeated until
                        this total time is reached. It may be exceeded if test
                        function is very slow or --benchmark-min-rounds is
                        large (it takes precedence). Default: '1.0'
  --benchmark-min-rounds=NUM
                        Minimum rounds, even if total time would exceed
                        `--max-time`. Default: 5
  --benchmark-timer=FUNC
                        Timer to use when measuring time. Default:
                        'time.perf_counter'
  --benchmark-calibration-precision=NUM
                        Precision to use when calibrating number of
                        iterations. Precision of 10 will make the timer look
                        10 times more accurate, at a cost of less precise
                        measure of deviations. Default: 10
  --benchmark-warmup=KIND
                        Activates warmup. Will run the test function up to
                        number of times in the calibration phase. See
                        `--benchmark-warmup-iterations`. Note: Even the warmup
                        phase obeys --benchmark-max-time. Available KIND:
                        'auto', 'off', 'on'. Default: 'auto' (automatically
                        activate on PyPy).
  --benchmark-warmup-iterations=NUM
                        Max number of iterations to run in the warmup phase.
                        Default: 100000
  --benchmark-disable-gc
                        Disable GC during benchmarks.
  --benchmark-skip      Skip running any tests that contain benchmarks.
  --benchmark-disable   Disable benchmarks. Benchmarked functions are only ran
                        once and no stats are reported. Use this is you want
                        to run the test but don't do any benchmarking.
  --benchmark-enable    Forcibly enable benchmarks. Use this option to
                        override --benchmark-disable (in case you have it in
                        pytest configuration).
  --benchmark-only      Only run benchmarks.
  --benchmark-save=NAME
                        Save the current run into 'STORAGE-PATH/counter-
                        NAME.json'. Default: '<commitid>_<date>_<time>_<isdirty>', example:
                        'e689af57e7439b9005749d806248897ad550eab5_20150811_041632_uncommitted-changes'.
  --benchmark-autosave  Autosave the current run into 'STORAGE-PATH/<counter>_<commitid>_<date>_<time>_<isdirty>',
                        example:
                        'STORAGE-PATH/0123_525685bcd6a51d1ade0be75e2892e713e02dfd19_20151028_221708_uncommitted-changes.json'
  --benchmark-save-data
                        Use this to make --benchmark-save and --benchmark-
                        autosave include all the timing data, not just the
                        stats.
  --benchmark-json=PATH
                        Dump a JSON report into PATH. Note that this will
                        include the complete data (all the timings, not just
                        the stats).
  --benchmark-compare=NUM
                        Compare the current run against run NUM (or prefix of
                        _id in elasticsearch) or the latest saved run if
                        unspecified.
  --benchmark-compare-fail=EXPR
                        Fail test if performance regresses according to given
                        EXPR (eg: min:5% or mean:0.001 for number of seconds).
                        Can be used multiple times.
  --benchmark-cprofile=COLUMN
                        If specified measure one run with cProfile and stores
                        10 top functions. Argument is a column to sort by.
                        Available columns: 'ncallls_recursion', 'ncalls',
                        'tottime', 'tottime_per', 'cumtime', 'cumtime_per',
                        'function_name'.
  --benchmark-storage=URI
                        Specify a path to store the runs as uri in form
                        file://path or elasticsearch+http[s]://host1,host2/[in
                        dex/doctype?project_name=Project] (when --benchmark-
                        save or --benchmark-autosave are used). For backwards
                        compatibility unexpected values are converted to
                        file://<value>. Default: 'file://./.benchmarks'.
  --benchmark-netrc=BENCHMARK_NETRC
                        Load elasticsearch credentials from a netrc file.
                        Default: ''.
  --benchmark-verbose   Dump diagnostic and progress information.
  --benchmark-sort=COL  Column to sort on. Can be one of: 'min', 'max',
                        'mean', 'stddev', 'name', 'fullname'. Default: 'min'
  --benchmark-group-by=LABEL
                        How to group tests. Can be one of: 'group', 'name',
                        'fullname', 'func', 'fullfunc', 'param' or
                        'param:NAME', where NAME is the name passed to
                        @pytest.parametrize. Default: 'group'
  --benchmark-columns=LABELS
                        Comma-separated list of columns to show in the result
                        table. Default: 'min, max, mean, stddev, median, iqr,
                        outliers, rounds, iterations'
  --benchmark-name=FORMAT
                        How to format names in results. Can be one of 'short',
                        'normal', 'long', or 'trial'. Default: 'normal'
  --benchmark-histogram=FILENAME-PREFIX
                        Plot graphs of min/max/avg/stddev over time in
                        FILENAME-PREFIX-test_name.svg. If FILENAME-PREFIX
                        contains slashes ('/') then directories will be
                        created. Default: 'benchmark_<date>_<time>'

Comparison CLI
--------------

An extra ``py.test-benchmark`` bin is available for inspecting previous benchmark data::

    py.test-benchmark [-h [COMMAND]] [--storage URI] [--netrc [NETRC]]
                      [--verbose]
                      {help,list,compare} ...

    Commands:
        help       Display help and exit.
        list       List saved runs.
        compare    Compare saved runs.

The compare ``command`` takes almost all the ``--benchmark`` options, minus the prefix:

    positional arguments:
      glob_or_file          Glob or exact path for json files. If not specified
                            all runs are loaded.

    optional arguments:
      -h, --help            show this help message and exit
      --sort=COL            Column to sort on. Can be one of: 'min', 'max',
                            'mean', 'stddev', 'name', 'fullname'. Default: 'min'
      --group-by=LABEL      How to group tests. Can be one of: 'group', 'name',
                            'fullname', 'func', 'fullfunc', 'param' or
                            'param:NAME', where NAME is the name passed to
                            @pytest.parametrize. Default: 'group'
      --columns=LABELS      Comma-separated list of columns to show in the result
                            table. Default: 'min, max, mean, stddev, median, iqr,
                            outliers, rounds, iterations'
      --name=FORMAT         How to format names in results. Can be one of 'short',
                            'normal', 'long', or 'trial'. Default: 'normal'
      --histogram=FILENAME-PREFIX
                            Plot graphs of min/max/avg/stddev over time in
                            FILENAME-PREFIX-test_name.svg. If FILENAME-PREFIX
                            contains slashes ('/') then directories will be
                            created. Default: 'benchmark_<date>_<time>'
      --csv=FILENAME        Save a csv report. If FILENAME contains slashes ('/')
                            then directories will be created. Default:
                            'benchmark_<date>_<time>'

    examples:

        pytest-benchmark compare 'Linux-CPython-3.5-64bit/*'

            Loads all benchmarks ran with that interpreter. Note the special quoting that disables your shell's glob
            expansion.

        pytest-benchmark compare 0001

            Loads first run from all the interpreters.

        pytest-benchmark compare /foo/bar/0001_abc.json /lorem/ipsum/0001_sir_dolor.json

            Loads runs from exactly those files.

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


Extra info
==========

You can set arbirary values in the ``benchmark.extra_info`` dictionary, which
will be saved in the JSON if you use ``--benchmark-autosave`` or similar:

.. code-block:: python

    def test_my_stuff(benchmark):
        benchmark.extra_info['foo'] = 'bar'
        benchmark(time.sleep, 0.02)

Patch utilities
===============

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
<https://github.com/ionelmc/python-aspectlib>`_ (make sure you ``pip install aspectlib`` or ``pip install
pytest-benchmark[aspect]``):

.. sourcecode:: python

    def test_foo(benchmark):
        benchmark.weave(Foo.internal, lazy=True):
        f = Foo()
        f.run()

.. _pedantic: http://pytest-benchmark.readthedocs.org/en/latest/pedantic.html
