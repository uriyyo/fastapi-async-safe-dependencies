from typing import Optional, TypeVar

T = TypeVar("T")

_MARKER_ATTR = "__is_async_safe__"


def async_safe(dep: T) -> T:
    setattr(dep, _MARKER_ATTR, True)
    return dep


def async_unsafe(dep: T) -> T:
    setattr(dep, _MARKER_ATTR, False)
    return dep


def is_async_safe(dep: T) -> Optional[bool]:
    return getattr(dep, _MARKER_ATTR, None)


# TODO: Not sure if need this, maybe just remove it and force users to use `async_safe` decorator?
@async_safe
class AsyncSafeMixin:
    pass


__all__ = [
    "async_safe",
    "async_unsafe",
    "is_async_safe",
    "AsyncSafeMixin",
]
