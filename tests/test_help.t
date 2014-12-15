  $ py.test --help | grep -C 1 benchmark
  \s* (re)
  benchmark:
    --benchmark-max-time=BENCHMARK_MAX_TIME
                          Maximum time to spend in a benchmark (including
                          overhead).
    --benchmark-max-iterations=BENCHMARK_MAX_ITERATIONS
                          Maximum iterations to do.
    --benchmark-min-iterations=BENCHMARK_MIN_ITERATIONS
                          Minium iterations, even if total time would exceed
                          `max-time`.
    --benchmark-timer=BENCHMARK_TIMER
                          Timer to use when measuring time.
    --benchmark-disable-gc
                          Disable GC during benchmarks.
    --benchmark-skip      Skip running any benchmarks.
    --benchmark-only      Only run benchmarks.
  \s* (re)
