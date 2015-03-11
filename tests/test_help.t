  $ COLUMNS=140 py.test --help | grep -C 1 benchmark
  \s* (re)
  benchmark:
    --benchmark-min-time=BENCHMARK_MIN_TIME
                          Minimum time per round in seconds. Default: 0.000025
    --benchmark-max-time=BENCHMARK_MAX_TIME
                          Maximum time to spend in a benchmark in seconds. Default: 1.0
    --benchmark-min-rounds=BENCHMARK_MIN_ROUNDS
                          Minimum rounds, even if total time would exceed `--max-time`. Default: 5
    --benchmark-sort=BENCHMARK_SORT
                          Column to sort on. Can be one of: 'min', 'max', 'mean' or 'stddev'. Default: min
    --benchmark-timer=BENCHMARK_TIMER
                          Timer to use when measuring time. Default: .* (re)
    --benchmark-warmup    Activates warmup. Will run the test function up to number of times in the calibration phase. See `--benchmark-
                          warmup-iterations`.
    --benchmark-warmup-iterations=BENCHMARK_WARMUP_ITERATIONS
                          Max number of iterations to run in the warmup phase. Default: 100000
    --benchmark-verbose   Dump diagnostic and progress information.
    --benchmark-disable-gc
                          Disable GC during benchmarks.
    --benchmark-skip      Skip running any benchmarks.
    --benchmark-only      Only run benchmarks.
  \s* (re)
