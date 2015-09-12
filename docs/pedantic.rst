Pedantic mode
=============

``pytest-benchmark`` allows a special mode that doesn't do any automatic calibration. To make it clear it's only for
people that know exactly what they need it's called "pedantic".

.. sourcecode:: python

    def test_with_setup(benchmark):
        benchmark.pedantic(stuff, args=(1, 2, 3), kwargs={'foo': 'bar'}, iterations=10, rounds=100)

Reference
---------

.. py:function:: benchmark.pedantic(target, args=(), kwargs=None, setup=None, rounds=1, warmup_rounds=0, iterations=1)

    :type  target: callable
    :param target: Function to benchmark.

    :type  args: list or tuple
    :param args: Positional arguments to the ``target`` function.

    :type  kwargs: dict
    :param kwargs: Named arguments to the ``target`` function.

    :type  setup: callable
    :param setup: A function to call right before calling the ``target`` function.

        The setup function can also return the arguments for the function (in case you need to create new arguments every time).

        .. sourcecode:: python

            def test_with_setup(benchmark):
                def setup():
                    # can optionally return a (args, kwargs) tuple
                    return (1, 2, 3), {'foo': 'bar'}
                benchmark.pedantic(stuff, setup=setup, rounds=100)

        .. note::

            if you use a ``setup`` function then you cannot use the ``args``, ``kwargs`` and ``iterations`` options.

    :type  rounds: int
    :param rounds: Number of rounds to run.

    :type  iterations: int
    :param iterations:
        Number of iterations.

        In the non-pedantic mode (eg: ``benchmark(stuff, 1, 2, 3, foo='bar')``) the ``iterations`` is automatically chosen
        depending on what timer you have. In other words, be careful in what you chose for this option.

        The default value (``1``) is **unsafe** for benchmarking very fast functions that take under 100μs (100 microseconds).

    :type  warmup_rounds: int
    :param warmup_rounds: Number of warmup rounds.

        Set to non-zero to enable warmup. Warmup will run with the same number of iterations.

        Example: if you have ``iteration=5, warmup_rounds=10`` then your function will be called 50 times.
