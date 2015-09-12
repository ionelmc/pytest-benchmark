Pedantic mode
=============

``pytest-benchmark`` allows a special mode that doesn't do any automatic calibration. To make it clear it's only for
people that know exactly what they need it's called "pedantic".

.. sourcecode:: python

    def test_with_setup(benchmark):
        benchmark.pedantic(stuff, args=(1, 2, 3), kwargs={'foo': 'bar'}, iterations=10, rounds=100)

Reference
---------

Arguments (and defaults):

* ``args=()``
* ``kwargs=None``
* ``setup=None``
* ``rounds=1`` - Number of rounds to run.
* ``warmup_rounds=0`` - Set to non-zero to enable warmup.

  Warmup will run with the same number of iterations. Eg: if you have ``iteration=5, warmup_rounds=10`` then your
  function will be called 50 times.
* ``iterations=1`` - Number of iterations.

  In the non-pedantic mode (eg: ``benchmark(stuff, 1, 2, 3, foo='bar')``) the ``iterations``is automatically chosen
  depending on what timer you have. In other words, be careful in what you chose for this option.

  The default value (``1``) is **unsafe** for benchmarking very fast functions that take under 100μs (100 microseconds).

Using a ``setup`` function
--------------------------

The setup function can also return the arguments for the function (in case you need to create new arguments every time).

.. sourcecode:: python

    def test_with_setup(benchmark):
        benchmark.pedantic(stuff, setup=setup, rounds=100)

Note that if you use a ``setup`` function then you cannot use the ``args``, ``kwargs`` and ``iterations`` options.


