import pstats
from collections.abc import Hashable
from functools import cached_property
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypeAlias
from typing import TypedDict
from typing import TypeVar

from .fixture import BenchmarkFixture

_D = TypeVar('_D')

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

class _MetadataDict_stats(_StatsDict):
    iterations: int
    data: NotRequired[list[float]]

class _MetadataDict(TypedDict):
    group: str | None
    name: str
    fullname: str
    params: dict[str, Any] | None
    param: str | None
    extra_info: dict[Hashable, Any]
    options: dict[str, Any]
    cprofile: NotRequired[list[_cprofile_stats]]
    stats: NotRequired[_MetadataDict_stats]

class _FlatMetadataDict(_MetadataDict, _StatsDict): ...

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


cProfileFilter: TypeAlias = tuple[cProfileStats | None, int]

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
    def get(self, key: str, default: _D = ...) -> Any | _D: ...
    def __getitem__(self, key: str) -> Any: ...
    @property
    def has_error(self) -> bool: ...
    def as_dict(
        self,
        include_data: bool = True,
        flat: bool = False,
        stats: bool = True,
        cprofile: cProfileFilter | None = ...,
    ) -> _MetadataDict | _FlatMetadataDict: ...
    def update(self, duration: float) -> None: ...

def normalize_stats(stats: Stats) -> Stats: ...
