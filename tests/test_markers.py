from pytest import mark

from fastapi_async_safe import AsyncSafeMixin, async_safe, async_unsafe
from fastapi_async_safe.markers import is_async_safe


@async_safe
def sync_func():
    pass


class FromMixinClass(AsyncSafeMixin):
    pass


@async_safe
class DecoratedClass(AsyncSafeMixin):
    pass


class InheritedFromMixinClass(FromMixinClass):
    pass


class InheritedFromDecoratedClass(DecoratedClass):
    pass


@mark.parametrize(
    "obj",
    [
        sync_func,
        FromMixinClass,
        DecoratedClass,
        InheritedFromMixinClass,
        InheritedFromDecoratedClass,
    ],
    ids=[
        "func",
        "mixin-class",
        "decorated-class",
        "inherited-from-mixin-class",
        "inherited-from-decorated-class",
    ],
)
def test_is_async_safe(obj):
    assert is_async_safe(obj)


def sync_func_unsafe():
    pass


class DefaultClass:
    pass


@async_unsafe
class InheritedFromMixinClassUnsafe(FromMixinClass):
    pass


@async_unsafe
class InheritedFromDecoratedClassUnsafe(DecoratedClass):
    pass


@mark.parametrize(
    "obj",
    [
        sync_func_unsafe,
        DefaultClass,
        InheritedFromMixinClassUnsafe,
        InheritedFromDecoratedClassUnsafe,
    ],
    ids=[
        "func",
        "default-class",
        "inherited-from-mixin-class",
        "inherited-from-decorated-class",
    ],
)
def test_is_async_unsafe(obj):
    assert not is_async_safe(obj)


@mark.parametrize(
    ("obj", "expected"),
    [
        (sync_func, True),
        (FromMixinClass, True),
        (DecoratedClass, True),
        (InheritedFromMixinClass, True),
        (InheritedFromDecoratedClass, True),
        (sync_func_unsafe, None),
        (DefaultClass, None),
        (InheritedFromMixinClassUnsafe, False),
        (InheritedFromDecoratedClassUnsafe, False),
    ],
    ids=[
        "func",
        "mixin-class",
        "decorated-class",
        "inherited-from-mixin-class",
        "inherited-from-decorated-class",
        "func-unsafe",
        "default-class",
        "inherited-from-mixin-class-unsafe",
        "inherited-from-decorated-class-unsafe",
    ],
)
def test_is_marked_with_async_safe(obj, expected):
    assert is_async_safe(obj) is expected
