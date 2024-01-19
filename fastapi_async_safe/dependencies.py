from contextlib import asynccontextmanager
from functools import partial
from typing import Any, AsyncIterator, Iterator, TypeVar

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, APIRouter

from .decorators import is_async_safe_wrapper, safe_async_wrapper
from .markers import is_async_safe


def _all_dependencies(dependant: Dependant) -> Iterator[Dependant]:
    yield dependant

    for dep in dependant.dependencies:
        yield from _all_dependencies(dep)


def wrap_dependant(dependant: Dependant) -> bool:
    call = dependant.call

    if call is None:  # pragma: no cover
        return False

    if is_async_safe_wrapper(call):
        return False

    if not is_async_safe(call):
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


def wrap_dependencies(holder: THasRoutes) -> None:
    router = _get_router(holder)

    for route in router.routes:
        if not isinstance(route, APIRoute):
            continue

        for dependant in _all_dependencies(route.dependant):
            wrap_dependant(dependant)


@asynccontextmanager
async def _lifespan_wrapper(base_lifespan: Any, app: THasRoutes) -> AsyncIterator[Any]:
    router = _get_router(app)
    wrap_dependencies(router)

    async with base_lifespan(app) as state:
        yield state


def init_app(root: THasRoutes) -> THasRoutes:
    router = _get_router(root)
    router.lifespan_context = partial(_lifespan_wrapper, router.lifespan_context)

    return root


__all__ = [
    "init_app",
    "wrap_dependant",
    "wrap_dependencies",
]
