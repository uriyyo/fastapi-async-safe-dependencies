from contextlib import asynccontextmanager
from typing import AsyncIterator

from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient


@asynccontextmanager
async def app_ctx(
    app: FastAPI,
    /,
) -> AsyncIterator[AsyncClient]:
    async with LifespanManager(app):  # noqa: SIM117
        async with AsyncClient(app=app, base_url="http://test.com/", follow_redirects=True) as client:
            yield client


__all__ = [
    "app_ctx",
]
