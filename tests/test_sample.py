from functools import partial

import pytest


empty = object()


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


class SimpleProxy(object):
    def __init__(self, factory):
        self.factory = factory
        self.object = empty

    def __str__(self):
        if self.object is empty:
            self.object = self.factory()
        return str(self.object)


class CachedPropertyProxy(object):
    def __init__(self, factory):
        self.factory = factory

    @cached_property
    def object(self):
        return self.factory()

    def __str__(self):
        return str(self.object)


class LocalsSimpleProxy(object):
    def __init__(self, factory):
        self.factory = factory
        self.object = empty

    def __str__(self, func=str):
        if self.object is empty:
            self.object = self.factory()
        return func(self.object)


class LocalsCachedPropertyProxy(object):
    def __init__(self, factory):
        self.factory = factory

    @cached_property
    def object(self):
        return self.factory()

    def __str__(self, func=str):
        return func(self.object)


@pytest.fixture(scope="module", params=["SimpleProxy", "CachedPropertyProxy", "LocalsSimpleProxy", "LocalsCachedPropertyProxy"])
def impl(request):
    return globals()[request.param]


def test_proto(benchmark, impl):
    obj = "foobar"
    proxied = impl(lambda: obj)
    result = benchmark(partial(str, proxied))
    assert result == obj
