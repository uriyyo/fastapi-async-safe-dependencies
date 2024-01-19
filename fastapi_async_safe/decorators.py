import inspect
from functools import wraps
from typing import Awaitable, Callable, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def safe_async_wrapper(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return func(*args, **kwargs)

    wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
    wrapper.__is_async_safe_wrapper__ = True  # type: ignore[attr-defined]
    return wrapper


def is_async_safe_wrapper(func: Callable[P, T]) -> bool:
    return getattr(func, "__is_async_safe_wrapper__", False)


__all__ = [
    "safe_async_wrapper",
    "is_async_safe_wrapper",
]
