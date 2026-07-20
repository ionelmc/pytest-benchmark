"""
..
  PYTEST_DONT_REWRITE
"""

import cProfile
import gc
import pstats
import statistics  # noqa: F401 - compatibility export consumed by session.py
import sys
import time
from cProfile import Profile
from math import ceil
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import ParamSpec
from typing import Protocol
from typing import Self
from typing import TypeVar
from typing import cast

import pytest

from .logger import Logger
from .stats import Metadata
from .timers import Timer
from .timers import compute_timer_precision
from .utils import NameWrapper
from .utils import format_time
from .utils import slugify

statistics_error: str | None = None
P = ParamSpec('P')
R = TypeVar('R')
Arguments = tuple[tuple[Any, ...], dict[str, Any]]
Runner = Callable[[range | None], float | tuple[float, Any]]


class CallSpec(Protocol):
    id: str
    params: dict[str, object]


class Rollback(Protocol):
    def rollback(self) -> None: ...


class FixtureAlreadyUsed(Exception):
    pass


class _NotSet:
    pass


class PauseInstrumentation:
    def __init__(self: Self, tracer: bool = True, profiler: bool = True) -> None:
        self.disable_profiler = profiler
        self.disable_tracer = tracer
        self.prev_tracer: Any = None
        self.prev_profiler: Any = None

    def __enter__(self) -> Self:
        if self.disable_tracer:
            self.prev_tracer = sys.gettrace()

            if self.prev_tracer:
                sys.settrace(None)

        if self.disable_profiler:
            self.prev_profiler = sys.getprofile()

            if self.prev_profiler:
                sys.setprofile(None)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.prev_tracer:
            sys.settrace(self.prev_tracer)

        if self.prev_profiler:
            sys.setprofile(self.prev_profiler)


class BenchmarkFixture:
    _precisions: ClassVar[dict[str, float]] = {}

    def __init__(
        self,
        node: pytest.Item,
        disable_gc: bool,
        timer: NameWrapper,
        min_rounds: int,
        min_time: float | int,
        max_time: float | int,
        warmup: bool,
        warmup_iterations: int,
        calibration_precision: int,
        add_stats: Callable[[Metadata], None],
        logger: Logger,
        warner: Callable[[Warning], None],
        disabled: bool,
        cprofile: str,
        cprofile_loops: int | None,
        cprofile_dump: str | None,
        group: str | None = None,
    ) -> None:
        self.name = node.name
        self.fullname = node._nodeid
        self.disabled = disabled
        self.param: str | None
        self.params: dict[str, object] | None
        if hasattr(node, 'callspec'):
            callspec = cast(CallSpec, node.callspec)
            self.param = callspec.id
            self.params = callspec.params
        else:
            self.param = None
            self.params = None
        self.group = group
        self.has_error: bool = False
        self.extra_info: dict[str, Any] = {}
        self.skipped: bool = False

        self._disable_gc = disable_gc
        self._timer = cast(Timer, timer.target)
        self._min_rounds = min_rounds
        self._max_time = float(max_time)
        self._min_time = float(min_time)
        self._add_stats = add_stats
        self._calibration_precision = calibration_precision
        self._warmup = warmup and warmup_iterations
        self._logger = logger
        self._warner = warner
        self._cleanup_callbacks: list[Callable[[], None]] = []
        self._mode: str | None = None
        self.cprofile = cprofile
        self.cprofile_loops = cprofile_loops
        self.cprofile_dump = cprofile_dump
        self.cprofile_stats = None
        self.stats: Metadata | None = None

    @property
    def enabled(self) -> bool:
        return not self.disabled

    def _get_precision(self, timer: Timer) -> float:
        timer_name = str(NameWrapper(timer))
        if timer_name in self._precisions:
            timer_precision = self._precisions[timer_name]

        else:
            timer_precision = compute_timer_precision(timer) or 0.0
            self._precisions[timer_name] = timer_precision
            self._logger.debug('')
            self._logger.debug(f'Computing precision for {NameWrapper(timer)} ... {format_time(timer_precision)}s.', blue=True, bold=True)
        return timer_precision

    def _make_runner(self, function_to_benchmark: Callable[..., R], args: tuple[Any, ...], kwargs: dict[str, Any]) -> Runner:
        def runner(loops_range: range | None, timer: Timer = self._timer) -> float | tuple[float, R]:
            gc_enabled = gc.isenabled()
            if self._disable_gc:
                gc.disable()
            try:
                if loops_range:
                    start = timer()

                    for _ in loops_range:
                        function_to_benchmark(*args, **kwargs)

                    end = timer()
                    return end - start

                else:
                    start = timer()
                    result = function_to_benchmark(*args, **kwargs)
                    end = timer()
                    return end - start, result

            finally:
                if gc_enabled:
                    gc.enable()

        return runner

    def _make_stats(self, iterations: int) -> Metadata:
        bench_stats = Metadata(
            self,
            iterations=iterations,
            options={
                'disable_gc': self._disable_gc,
                'timer': self._timer,
                'min_rounds': self._min_rounds,
                'max_time': self._max_time,
                'min_time': self._min_time,
                'warmup': self._warmup,
            },
        )
        self._add_stats(bench_stats)
        self.stats = bench_stats
        return bench_stats

    def _save_cprofile(self, profile: Profile) -> None:
        stats = pstats.Stats(profile)
        assert self.stats is not None
        self.stats.cprofile_stats = stats

        if self.cprofile_dump:
            output_file = Path(f'{self.cprofile_dump}-{slugify(self.name)}.prof')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            stats.dump_stats(output_file)
            self._logger.info(f'Saved profile: {output_file}', bold=True)

    def __call__(self, function_to_benchmark: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        if self._mode:
            self.has_error = True
            raise FixtureAlreadyUsed(f'Fixture can only be used once. Previously it was used in {self._mode} mode.')

        try:
            self._mode = 'benchmark(...)'
            return self._raw(function_to_benchmark, *args, **kwargs)

        except Exception:
            self.has_error = True
            raise

    def pedantic(
        self,
        target: Callable[..., R],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        setup: Callable[[], Arguments | None] | None = None,
        teardown: Callable[..., None] | None = None,
        rounds: int = 1,
        warmup_rounds: int = 0,
        iterations: int = 1,
    ) -> R:
        if self._mode:
            self.has_error = True
            raise FixtureAlreadyUsed(f'Fixture can only be used once. Previously it was used in {self._mode} mode.')

        try:
            self._mode = 'benchmark.pedantic(...)'
            return self._raw_pedantic(
                target,
                args=args,
                kwargs=kwargs,
                setup=setup,
                teardown=teardown,
                rounds=rounds,
                warmup_rounds=warmup_rounds,
                iterations=iterations,
            )
        except Exception:
            self.has_error = True
            raise

    def _raw(self, function_to_benchmark: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
        loops_range = None

        if self.enabled:
            runner = self._make_runner(function_to_benchmark, args, kwargs)

            with PauseInstrumentation():
                duration, iterations, loops_range = self._calibrate_timer(runner)

            # Choose how many times we must repeat the test
            rounds = ceil(self._max_time / duration)
            rounds = max(rounds, self._min_rounds)
            rounds = min(rounds, sys.maxsize)

            stats = self._make_stats(iterations)

            self._logger.debug(f'  Running {rounds} rounds x {iterations} iterations ...', yellow=True, bold=True)
            run_start = time.time()
            if self._warmup:
                warmup_rounds = min(rounds, max(1, int(self._warmup / iterations)))
                self._logger.debug(f'  Warmup {warmup_rounds} rounds x {iterations} iterations ...')
                with PauseInstrumentation():
                    for _ in range(warmup_rounds):
                        runner(loops_range)
            with PauseInstrumentation():
                for _ in range(rounds):
                    stats.update(cast(float, runner(loops_range)))
            self._logger.debug(f'  Ran for {format_time(time.time() - run_start)}s.', yellow=True, bold=True)
        if self.cprofile_loops is None:
            cprofile_loops = loops_range or range(1)
        else:
            cprofile_loops = range(self.cprofile_loops)
        if self.enabled and self.cprofile:
            with PauseInstrumentation():
                profile = cProfile.Profile()
                cprofile_iterator = iter(cprofile_loops)
                next(cprofile_iterator)
                function_result = profile.runcall(function_to_benchmark, *args, **kwargs)
                for _ in cprofile_iterator:
                    function_result = profile.runcall(function_to_benchmark, *args, **kwargs)
                self._save_cprofile(profile)
        else:
            function_result = function_to_benchmark(*args, **kwargs)
        return function_result

    def _raw_pedantic(
        self,
        target: Callable[..., R],
        args: tuple[Any, ...] = (),
        kwargs: dict[str, Any] | None = None,
        setup: Callable[[], Arguments | None] | None = None,
        teardown: Callable[..., None] | None = None,
        rounds: int = 1,
        warmup_rounds: int = 0,
        iterations: int = 1,
    ) -> R:
        if kwargs is None:
            kwargs = {}
        benchmark_kwargs = kwargs

        has_args = bool(args or benchmark_kwargs)

        if not isinstance(iterations, int) or iterations < 1:
            raise ValueError('Must have positive int for `iterations`.')

        if not isinstance(rounds, int) or rounds < 1:
            raise ValueError('Must have positive int for `rounds`.')

        if not isinstance(warmup_rounds, int) or warmup_rounds < 0:
            raise ValueError('Must have positive int for `warmup_rounds`.')

        if iterations > 1 and setup:
            raise ValueError("Can't use more than 1 `iterations` with a `setup` function.")

        def make_arguments(args: tuple[Any, ...] = args, kwargs: dict[str, Any] = benchmark_kwargs) -> Arguments:
            if setup:
                maybe_args = setup()
                if maybe_args:
                    if has_args:
                        raise TypeError("Can't use `args` or `kwargs` if `setup` returns the arguments.")
                    args, kwargs = maybe_args
            return args, kwargs

        if self.disabled:
            args, kwargs = make_arguments()
            return target(*args, **kwargs)

        stats = self._make_stats(iterations)
        loops_range = range(iterations) if iterations > 1 else None
        result: R | _NotSet = _NotSet()
        for _ in range(warmup_rounds):
            args, kwargs = make_arguments()

            runner = self._make_runner(target, args, kwargs)
            with PauseInstrumentation():
                runner(loops_range)

            if teardown is not None:
                teardown(*args, **kwargs)

        for _ in range(rounds):
            args, kwargs = make_arguments()

            runner = self._make_runner(target, args, kwargs)
            with PauseInstrumentation():
                if loops_range:
                    duration = cast(float, runner(loops_range))
                else:
                    duration, result = cast(tuple[float, R], runner(loops_range))
            stats.update(duration)

            if teardown is not None:
                teardown(*args, **kwargs)

        if loops_range:
            # if it has been looped then we don't have the result, we need to do 1 extra run for it
            args, kwargs = make_arguments()
            result = target(*args, **kwargs)
            if teardown is not None:
                teardown(*args, **kwargs)

        if isinstance(result, _NotSet):
            raise RuntimeError('Benchmark target did not produce a result.')

        if self.cprofile:
            if self.cprofile_loops is None:
                cprofile_loops = loops_range or range(1)
            else:
                cprofile_loops = range(self.cprofile_loops)

            profile = cProfile.Profile()
            args, kwargs = make_arguments()
            for _ in cprofile_loops:
                with PauseInstrumentation():
                    profile.runcall(target, *args, **kwargs)
                if teardown is not None:
                    teardown(*args, **kwargs)
            self._save_cprofile(profile)

        return result

    def weave(self, target: Callable[P, R], **kwargs: Any) -> None:
        try:
            import aspectlib  # noqa: PLC0415
        except ImportError as exc:
            raise ImportError(exc.args, 'Please install aspectlib or pytest-benchmark[aspect]') from exc

        def aspect(function: Callable[P, R]) -> Callable[P, R]:
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return self(function, *args, **kwargs)

            return wrapper

        weave = cast(Callable[..., Rollback], aspectlib.weave)
        self._cleanup_callbacks.append(weave(target, aspect, **kwargs).rollback)

    patch = weave

    def _cleanup(self) -> None:
        while self._cleanup_callbacks:
            callback = self._cleanup_callbacks.pop()
            callback()
        if not self._mode and not self.skipped:
            self._logger.warning('Benchmark fixture was not used at all in this test!', warner=self._warner, suspend=True)

    def _calibrate_timer(self, runner: Runner) -> tuple[float, int, range]:
        timer_precision = self._get_precision(self._timer)
        min_time = max(self._min_time, timer_precision * self._calibration_precision)
        min_time_estimate = min_time * 5 / self._calibration_precision
        self._logger.debug('')
        self._logger.debug(
            f'  Calibrating to target round {format_time(min_time)}s; will estimate when reaching {format_time(min_time_estimate)}s '
            f'(using: {NameWrapper(self._timer)}, precision: {format_time(timer_precision)}s).',
            yellow=True,
            bold=True,
        )

        loops = 1
        while True:
            loops_range = range(loops)
            duration = cast(float, runner(loops_range))
            if self._warmup:
                warmup_start = time.time()
                warmup_iterations = 0
                warmup_rounds = 0
                while time.time() - warmup_start < self._max_time and warmup_iterations < self._warmup:
                    duration = min(duration, cast(float, runner(loops_range)))
                    warmup_rounds += 1
                    warmup_iterations += loops
                self._logger.debug(f'    Warmup: {format_time(time.time() - warmup_start)}s ({warmup_rounds} x {loops} iterations).')

            self._logger.debug(f'    Measured {loops} iterations: {format_time(duration)}s.', yellow=True)
            if duration >= min_time:
                break

            if duration >= min_time_estimate:
                # coarse estimation of the number of loops
                loops = ceil(min_time * loops / duration)
                self._logger.debug(f'    Estimating {loops} iterations.', green=True)
                if loops == 1:
                    # If we got a single loop then bail early - nothing to calibrate if the
                    # test function is 100 times slower than the timer resolution.
                    loops_range = range(loops)
                    break
            else:
                loops *= 10
        return duration, loops, loops_range
