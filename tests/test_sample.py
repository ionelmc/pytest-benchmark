from collections.abc import Callable
from functools import partial
from typing import Generic
from typing import TypeVar

import pytest

from pytest_benchmark.fixture import BenchmarkFixture

empty = object()


Owner = TypeVar('Owner')
Value = TypeVar('Value')


class cached_property(Generic[Owner, Value]):
    def __init__(self, func: Callable[[Owner], Value]) -> None:
        self.func = func

    def __get__(self, obj: Owner, cls: type[Owner] | None = None) -> Value:
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class SimpleProxy:
    def __init__(self, factory: Callable[[], object]) -> None:
        self.factory = factory
        self.object: object = empty

    def __str__(self):
        if self.object is empty:
            self.object = self.factory()
        return str(self.object)


class CachedPropertyProxy:
    def __init__(self, factory: Callable[[], object]) -> None:
        self.factory = factory

    @cached_property
    def object(self) -> object:
        return self.factory()

    def __str__(self):
        return str(self.object)


class LocalsSimpleProxy:
    def __init__(self, factory: Callable[[], object]) -> None:
        self.factory = factory
        self.object: object = empty

    def __str__(self, func=str):
        if self.object is empty:
            self.object = self.factory()
        return func(self.object)


class LocalsCachedPropertyProxy:
    def __init__(self, factory: Callable[[], object]) -> None:
        self.factory = factory

    @cached_property
    def object(self) -> object:
        return self.factory()

    def __str__(self, func=str):
        return func(self.object)


@pytest.fixture(scope='module', params=['SimpleProxy', 'CachedPropertyProxy', 'LocalsSimpleProxy', 'LocalsCachedPropertyProxy'])
def impl(
    request: pytest.FixtureRequest,
) -> type[SimpleProxy] | type[CachedPropertyProxy] | type[LocalsSimpleProxy] | type[LocalsCachedPropertyProxy]:
    implementations = {
        'SimpleProxy': SimpleProxy,
        'CachedPropertyProxy': CachedPropertyProxy,
        'LocalsSimpleProxy': LocalsSimpleProxy,
        'LocalsCachedPropertyProxy': LocalsCachedPropertyProxy,
    }
    assert isinstance(request.param, str)
    return implementations[request.param]


def test_proto(
    benchmark: BenchmarkFixture,
    impl: type[SimpleProxy] | type[CachedPropertyProxy] | type[LocalsSimpleProxy] | type[LocalsCachedPropertyProxy],
) -> None:
    obj = 'foobar'
    proxied = impl(lambda: obj)
    result = benchmark(partial(str, proxied))
    assert result == obj
