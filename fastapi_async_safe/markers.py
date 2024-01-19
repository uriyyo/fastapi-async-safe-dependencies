from typing import TypeVar

T = TypeVar("T")


def async_safe(dep: T) -> T:
    dep.__is_async_safe__ = True  # type: ignore[attr-defined]
    return dep


def async_unsafe(dep: T) -> T:
    dep.__is_async_safe__ = False  # type: ignore[attr-defined]
    return dep


def is_async_safe(dep: T) -> bool:
    return getattr(dep, "__is_async_safe__", False)


# TODO: Not sure if need this, we can only use `async_safe` decorator
@async_safe
class AsyncSafeMixin:
    pass


__all__ = [
    "async_safe",
    "async_unsafe",
    "is_async_safe",
    "AsyncSafeMixin",
]
