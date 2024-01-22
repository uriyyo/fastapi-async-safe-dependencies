import asyncio
from typing import Any, Coroutine, TypeVar

try:
    import uvloop
except ImportError:
    _run = asyncio.run
else:
    _run = uvloop.run

T = TypeVar("T")


def run(coro: Coroutine[Any, Any, T]) -> T:
    return _run(coro)


__all__ = [
    "run",
]
