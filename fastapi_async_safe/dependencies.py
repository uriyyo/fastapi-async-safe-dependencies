import asyncio
import inspect
from contextlib import asynccontextmanager
from functools import partial
from typing import Any, AsyncIterator, Iterator, Optional, Sequence, TypeVar

from fastapi import FastAPI
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute, APIRouter
from typing_extensions import TypeAlias

from .decorators import is_async_safe_wrapper, safe_async_wrapper
from .ext import extensions_predicate
from .markers import is_async_safe
from .types import DependantCall, DependantCallPredicate

_Predicates: TypeAlias = Optional[Sequence[DependantCallPredicate]]


def _all_dependencies(dependant: Dependant) -> Iterator[Dependant]:
    yield dependant

    for dep in dependant.dependencies:
        yield from _all_dependencies(dep)


def _should_wrap_dependant_call(
    call: DependantCall,
    all_classes_safe: Optional[bool] = None,
    predicates: _Predicates = None,
) -> bool:
    all_classes_safe = all_classes_safe or False

    # call is already wrapped with `safe_async_wrapper`, no need to wrap it again
    if is_async_safe_wrapper(call):
        return False

    # call is coroutine function, no need to wrap it
    if asyncio.iscoroutinefunction(call):
        return False

    # one of the predicates matched, so we will wrap it
    if any(predicate(call) for predicate in predicates or ()):
        return True

    # it's extension, so we will wrap it
    if extensions_predicate(call):
        return True

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
    predicates: _Predicates = None,
) -> bool:
    call = dependant.call

    # not sure if it's possible, but it marked as optional, so let have a check
    if call is None:  # pragma: no cover
        return False

    if not _should_wrap_dependant_call(call, all_classes_safe, predicates):
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
    predicates: _Predicates = None,
) -> None:
    router = _get_router(holder)

    for route in router.routes:
        if not isinstance(route, APIRoute):
            continue

        for dependant in _all_dependencies(route.dependant):
            wrap_dependant(dependant, all_classes_safe, predicates)


@asynccontextmanager
async def _lifespan_wrapper(
    app: THasRoutes,
    *,
    base_lifespan: Any,
    all_classes_safe: Optional[bool] = None,
    predicates: _Predicates = None,
) -> AsyncIterator[Any]:
    router = _get_router(app)
    wrap_dependencies(router, all_classes_safe, predicates)

    async with base_lifespan(app) as state:
        yield state


def init_app(
    root: THasRoutes,
    *,
    all_classes_safe: Optional[bool] = None,
    predicates: _Predicates = None,
) -> THasRoutes:
    router = _get_router(root)

    router.lifespan_context = partial(
        _lifespan_wrapper,
        base_lifespan=router.lifespan_context,
        all_classes_safe=all_classes_safe,
        predicates=predicates,
    )

    return root


__all__ = [
    "init_app",
    "wrap_dependant",
    "wrap_dependencies",
]
