import threading
from typing import Any

from fastapi import Depends, FastAPI

from fastapi_async_safe import async_safe, async_unsafe, init_app
from fastapi_async_safe.dependencies import wrap_dependant

from .utils import app_ctx


async def test_dependency_wrapped():
    app = FastAPI()
    init_app(app)

    calls = set()

    @async_safe
    def sync_func():
        calls.add(f"{threading.get_ident()}-sync_func")

    async def async_func():
        calls.add(f"{threading.get_ident()}-async_func")

    @async_safe
    class ClassDep:
        def __init__(self):
            calls.add(f"{threading.get_ident()}-ClassDep")

    @app.get("/")
    async def route(
        a: Any = Depends(sync_func),
        b: Any = Depends(ClassDep),
        c: Any = Depends(async_func),
    ):
        calls.add(f"{threading.get_ident()}-route")
        return {}

    async with app_ctx(app) as client:
        response = await client.get("/")
        response.raise_for_status()

    indent = threading.get_ident()

    assert calls == {
        f"{indent}-sync_func",
        f"{indent}-async_func",
        f"{indent}-ClassDep",
        f"{indent}-route",
    }


async def test_dependency_not_wrapped():
    app = FastAPI()
    init_app(app)

    indent = threading.get_ident()

    def sync_func():
        assert threading.get_ident() != indent

    async def async_func():
        assert threading.get_ident() == indent

    class ClassDep:
        def __init__(self):
            assert threading.get_ident() != indent

    @app.get("/")
    async def route(
        a: Any = Depends(sync_func),
        b: Any = Depends(ClassDep),
        c: Any = Depends(async_func),
    ):
        return {}

    async with app_ctx(app) as client:
        response = await client.get("/")
        response.raise_for_status()


async def test_predicates():
    app = FastAPI()
    init_app(app, predicates=[lambda f: f is sync_func])

    indent = threading.get_ident()

    def sync_func():
        assert threading.get_ident() == indent

    async def async_func():
        assert threading.get_ident() == indent

    @app.get("/")
    async def route(
        a: Any = Depends(sync_func),
        c: Any = Depends(async_func),
    ):
        return {}

    async with app_ctx(app) as client:
        response = await client.get("/")
        response.raise_for_status()


async def test_all_classes_safe():
    app = FastAPI()
    init_app(app, all_classes_safe=True)

    indent = threading.get_ident()

    class ClassDep:
        def __init__(self):
            assert threading.get_ident() == indent

    @async_unsafe
    class ClassDepUnSafe:
        def __init__(self):
            assert threading.get_ident() != indent

    @app.get("/")
    async def route(
        a: ClassDep = Depends(),
        b: ClassDepUnSafe = Depends(),
    ):
        return {}

    async with app_ctx(app) as client:
        response = await client.get("/")
        response.raise_for_status()


def test_double_wrapped():
    app = FastAPI()

    @async_safe
    def sync_func() -> None:
        pass

    @app.get("/")
    def _route(a: Any = Depends(sync_func)):
        return {}

    *_, route = app.routes
    (dependant,) = route.dependant.dependencies

    assert wrap_dependant(dependant)
    assert not wrap_dependant(dependant)
