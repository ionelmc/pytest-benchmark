import pstats
from collections.abc import Hashable
from functools import cached_property
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict
from typing import TypeVar
from typing import overload

from .fixture import BenchmarkFixture

# Typed Dicts for as_dict returns

class _StatsDict(TypedDict):
    min: float
    max: float
    mean: float
    stddev: float
    rounds: int
    median: float
    iqr: float
    q1: float
    q3: float
    iqr_outliers: int | str
    stddev_outliers: int
    outliers: int | str
    ld15iqr: float
    hd15iqr: float
    ops: float
    total: float

class _cprofile_stats(TypedDict):
    ncalls_recursion: str
    ncalls: int
    tottime: float
    tottime_per: float
    cumtime: float
    cumime_per: float
    function_name: str


# Each flag for Metadata.as_dict() can change the included keys

class _MetadataDict(TypedDict):
    group: str | None
    name: str
    fullname: str
    params: dict[str, Any] | None
    param: str | None
    extra_info: dict[Hashable, Any]
    options: dict[str, Any]
    cprofile: NotRequired[list[_cprofile_stats]]

class _MetadataDict_stats(_StatsDict):
    iterations: int

class _MetadataDict_stats_data(_MetadataDict_stats):
    data: list[float]

class _MetadataDict_stats_flat(_MetadataDict, _MetadataDict_stats): ...
class _MetadataDict_stats_data_flat(_MetadataDict, _MetadataDict_stats_data): ...

class _MetadataDict_stats_nonflat(_MetadataDict):
    stats: _MetadataDict_stats
class _MetadataDict_stats_data_nonflat(_MetadataDict):
    stats: _MetadataDict_stats_data


cProfileStats = Literal[
    'cumtime',
    'tottime',
    'ncalls',
    'ncalls_recursion',
    'tottime_per',
    'cumtime_per',
    'function_name',
]

Field = Literal[
    'min',
    'max',
    'mean',
    'stddev',
    'rounds',
    'median',
    'iqr',
    'q1',
    'q3',
    'iqr_outliers',
    'stddev_outliers',
    'outliers',
    'ld15iqr',
    'hd15iqr',
    'ops',
    'total',
]

class Stats:
    fields: tuple[Field, ...]

    def __init__(self) -> None:
        self.data: list[float]

    def __bool__(self) -> bool: ...
    def __nonzero__(self) -> bool: ...
    def as_dict(self) -> _StatsDict: ...
    def update(self, duration: float) -> None: ...
    @cached_property
    def sorted_data(self) -> list[float]: ...
    @cached_property
    def total(self) -> float: ...
    @cached_property
    def min(self) -> float: ...
    @cached_property
    def max(self) -> float: ...
    @cached_property
    def mean(self) -> float: ...
    @cached_property
    def stddev(self) -> float: ...
    @property
    def stddev_outliers(self) -> int: ...
    @cached_property
    def rounds(self) -> int: ...
    @cached_property
    def median(self) -> float: ...
    @cached_property
    def ld15iqr(self) -> float: ...
    @cached_property
    def hd15iqr(self) -> float: ...
    @cached_property
    def q1(self) -> float: ...
    @cached_property
    def q3(self) -> float: ...
    @cached_property
    def iqr(self) -> float: ...
    @cached_property
    def iqr_outliers(self) -> int: ...
    @cached_property
    def outliers(self) -> str: ...
    @cached_property
    def ops(self) -> float: ...

class Metadata:
    _D = TypeVar('_D')

    def __init__(self, fixture: BenchmarkFixture, iterations: int, options: dict[str, Any]) -> None:
        self.name: str
        self.fullname: str
        self.group: str | None
        self.param: str | None
        self.params: dict[str, Any] | None
        self.extra_info: dict[Hashable, Any]
        self.cprofile_stats: pstats.Stats | None

        self.iterations: int
        self.stats: Stats | None
        self.options: dict[str, Any]
        self.fixture: BenchmarkFixture

    def __bool__(self) -> bool: ...
    def __nonzero__(self) -> bool: ...
    def get(self, key: str, default: _D = None) -> Any | _D: ...
    def __getitem__(self, key: str) -> Any: ...
    @property
    def has_error(self) -> bool: ...
    @overload
    def as_dict( # no stats
        self,
        include_data: bool = ...,
        flat: bool = ...,
        stats: Literal[False] = False,
        cprofile: tuple[cProfileStats | None, int] | None = ...,
    ) -> _MetadataDict: ...
    @overload
    def as_dict( # stats
        self,
        include_data: Literal[False] = False,
        flat: Literal[False] = False,
        stats: Literal[True] = True,
        cprofile: tuple[cProfileStats | None, int] | None = ...,
    ) -> _MetadataDict_stats_nonflat: ...
    @overload
    def as_dict( # flat stats
        self,
        include_data: Literal[False] = False,
        flat: Literal[True] = True,
        stats: Literal[True] = True,
        cprofile: tuple[cProfileStats | None, int] | None = ...,
    ) -> _MetadataDict_stats_flat: ...
    @overload
    def as_dict( # stats with data
        self,
        include_data: Literal[True] = True,
        flat: Literal[False] = False,
        stats: Literal[True] = True,
        cprofile: tuple[cProfileStats | None, int] | None = ...,
    ) -> _MetadataDict_stats_data_nonflat: ...
    @overload
    def as_dict( # flat stats with data
        self,
        include_data: Literal[True] = True,
        flat: Literal[True] = True,
        stats: Literal[True] = True,
        cprofile: tuple[cProfileStats | None, int] | None = ...,
    ) -> _MetadataDict_stats_data_flat: ...
    def update(self, duration: float) -> None: ...

def normalize_stats(stats: Stats) -> Stats: ...
