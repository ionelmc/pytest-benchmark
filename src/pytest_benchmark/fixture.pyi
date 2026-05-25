import cProfile
import pstats
from collections.abc import Callable
from collections.abc import Hashable
from typing import Any
from typing import ParamSpec
from typing import TypeAlias
from typing import TypeVar
from typing import overload

from .stats import Metadata

statistics: Any
statistics_error: str | None

_Args: TypeAlias = tuple[Any, ...] | tuple[()]
_Kwargs: TypeAlias = dict[str, Any]
_SetupFunc: TypeAlias = Callable[..., tuple[_Args, _Kwargs]]
_TeardownFunc: TypeAlias = Callable[..., Any]

_P = ParamSpec('_P')
_R = TypeVar('_R')

class BenchmarkFixture:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.name: str
        self.fullname: str
        self.disabled: bool
        self.param: str | None
        self.params: dict[str, Any] | None
        self.group: str | None
        self.has_error: bool
        self.extra_info: dict[Hashable, Any]
        self.skipped: bool

        self.cprofile: cProfile.Profile
        self.cprofile_loops: int | None
        self.cprofile_dump: str | None

        self.cprofile_stats: pstats.Stats | None
        self.stats: Metadata | None

    @property
    def enabled(self) -> bool: ...
    def __call__(  # Expose `function_to_benchmark` *args/**kwargs to `__call__`
        self,
        function_to_benchmark: Callable[_P, _R],
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> _R: ...
    @overload
    def pedantic(  # Provided `args` and/or `kwargs` (prevent `setup`)
        self,
        target: Callable[_P, _R],
        args: _Args = ...,
        kwargs: _Kwargs | None = ...,
        *,
        teardown: _TeardownFunc | None = ...,
        rounds: int = ...,
        warmup_rounds: int = ...,
        iterations: int = ...,
    ) -> _R: ...
    @overload
    def pedantic(  # Provided `setup` (prevent `args`/`kwargs`)
        self,
        target: Callable[_P, _R],
        *,
        setup: _SetupFunc | None = ...,
        teardown: _TeardownFunc | None = ...,
        rounds: int = ...,
        warmup_rounds: int = ...,
        iterations: int = ...,
    ) -> _R: ...
    def weave(
        self,
        target: Callable[_P, _R],
        **kwargs: Any,
    ) -> None: ...

    patch = weave
