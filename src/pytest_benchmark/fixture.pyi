from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Never, overload

if TYPE_CHECKING:
    import cProfile


# Compound Types
type Args = tuple[Any, ...] | tuple[Never]
type Kwargs = dict[str, Any]
type SetupFunc = Callable[[], tuple[tuple[Any, ...], dict[str, Any]]]
type TeardownFunc = Callable[[], Any]


class BenchmarkFixture:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.name: str
        self.fullname: str
        self.disabled: bool
        self.param: str | None
        self.params: tuple[str, ...] | None
        self.group: str | None
        self.has_error: bool
        self.extra_info: dict[str, Any]
        self.skipped: bool

        self.cprofile: cProfile.Profile
        self.cprofile_loops: int | None
        self.cprofile_dump: str | None
        
        # Narrow types for stats?
        self.cprofile_stats: dict[Any, Any] | None
        self.stats: dict[Any, Any] | None 

    @property
    def enabled(self) -> bool: ...

    # Expose `function_to_benchmark` *args/**kwargs to `__call__`
    def __call__[**P, R](self, function_to_benchmark: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R: ...

    # Provided `args` and/or `kwargs` (prevent `setup`)
    @overload
    def pedantic[**P, R](self, target: Callable[P, R], 
                         args: Args, kwargs: Kwargs | None,
                         *, 
                         teardown: TeardownFunc| None=..., rounds: int=..., warmup_rounds: int=..., iterations: int=...) -> R: ...
    # Provided `setup` (prevent `args`/`kwargs`)
    @overload
    def pedantic[**P, R](self, target: Callable[P, R], 
                         *,
                         setup: SetupFunc, 
                         teardown: Callable[[], Any] | None=..., rounds: int=..., warmup_rounds: int=..., iterations: int=...) -> R: ...
    def pedantic[**P, R](
            self, 
            target: Callable[P, R], 
            args: Args = (), 
            kwargs: Kwargs | None = None, 
            setup: SetupFunc | None = None, 
            teardown: TeardownFunc | None = None, 
            rounds: int = 1, 
            warmup_rounds: int = 0, 
            iterations: int = 1
        ) -> R: ...
    
    def weave[**P, R](self, target: Callable[P, R], **kwargs: Any) -> None: ...

    patch = weave