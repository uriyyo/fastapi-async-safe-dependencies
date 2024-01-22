import asyncio
import inspect
from contextlib import asynccontextmanager
from functools import partial
from typing import Any, AsyncIterator, Callable, Iterator, Optional, TypeVar

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, APIRouter

from .decorators import is_async_safe_wrapper, safe_async_wrapper
from .markers import is_async_safe


def _all_dependencies(dependant: Dependant) -> Iterator[Dependant]:
    yield dependant

    for dep in dependant.dependencies:
        yield from _all_dependencies(dep)


def _should_wrap_dependant_call(
    call: Callable[..., Any],
    all_classes_safe: Optional[bool] = None,
) -> bool:
    all_classes_safe = all_classes_safe or False

    # call is already wrapped with `safe_async_wrapper`, no need to wrap it again
    if is_async_safe_wrapper(call):
        return False

    # call is coroutine function, no need to wrap it
    if asyncio.iscoroutinefunction(call):
        return False

    # we treat all classes as async safe, this call is class, and it is not marked with `async_safe`/`async_unsafe`
    # so we can safely wrap it with `safe_async_wrapper`
    if all_classes_safe and inspect.isclass(call) and is_async_safe(call) is None:
        return True

    # call is not async safe, it not safe to wrap it with `safe_async_wrapper`
    if not is_async_safe(call):
        return False

    return True


def wrap_dependant(
    dependant: Dependant,
    all_classes_safe: Optional[bool] = None,
) -> bool:
    call = dependant.call

    # not sure if it's possible, but it marked as optional, so let have a check
    if call is None:  # pragma: no cover
        return False

    if not _should_wrap_dependant_call(call, all_classes_safe):
        return False

    wrapped = safe_async_wrapper(dependant.call)  # type: ignore[arg-type]

    dependant.call = wrapped
    dependant.cache_key = (wrapped, dependant.cache_key[1])

    return True


THasRoutes = TypeVar("THasRoutes", APIRouter, FastAPI)


def _get_router(root: THasRoutes) -> APIRouter:
    if isinstance(root, FastAPI):
        return root.router

    return root


def wrap_dependencies(
    holder: THasRoutes,
    all_classes_safe: Optional[bool] = None,
) -> None:
    router = _get_router(holder)

    for route in router.routes:
        if not isinstance(route, APIRoute):
            continue

        for dependant in _all_dependencies(route.dependant):
            wrap_dependant(dependant, all_classes_safe)


@asynccontextmanager
async def _lifespan_wrapper(
    app: THasRoutes,
    *,
    base_lifespan: Any,
    all_classes_safe: Optional[bool] = None,
) -> AsyncIterator[Any]:
    router = _get_router(app)
    wrap_dependencies(router, all_classes_safe)

    async with base_lifespan(app) as state:
        yield state


def init_app(
    root: THasRoutes,
    *,
    all_classes_safe: Optional[bool] = None,
) -> THasRoutes:
    router = _get_router(root)

    router.lifespan_context = partial(
        _lifespan_wrapper,
        base_lifespan=router.lifespan_context,
        all_classes_safe=all_classes_safe,
    )

    return root


__all__ = [
    "init_app",
    "wrap_dependant",
    "wrap_dependencies",
]
