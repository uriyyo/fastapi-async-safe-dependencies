from asyncio import sleep
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

from fastapi import APIRouter, Depends, FastAPI, Query

from fastapi_async_safe import async_safe, init_app

router = APIRouter()


class DB:
    async def get(self) -> Any:
        await sleep(0)  # simulate db call, just will switch to another task
        return {"hello": "world"}


async def get_db() -> AsyncIterator[DB]:
    yield DB()


@async_safe
class Dependency:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        dataclass(cls)


class UserRepository(Dependency):
    db: DB = Depends(get_db)

    async def get(self) -> Any:
        return await self.db.get()


class GroupRepository(Dependency):
    db: DB = Depends(get_db)

    async def get(self) -> Any:
        return await self.db.get()


class UserService(Dependency):
    user_repo: UserRepository = Depends()

    async def get(self) -> Any:
        return await self.user_repo.get()


class GroupService(Dependency):
    group_repo: GroupRepository = Depends()

    async def get(self) -> Any:
        return await self.group_repo.get()


class CommonFilterParams(Dependency):
    name: Optional[str] = Query(None, min_length=1, max_length=255)
    age: Optional[int] = Query(None, ge=0, le=100)


async def get_current_user(
    user_service: UserService = Depends(),
) -> Any:
    return await user_service.get()


async def get_current_group(
    group_service: GroupService = Depends(),
) -> Any:
    return await group_service.get()


@router.get("/")
async def get_users(
    current_user: Any = Depends(get_current_user),
    current_group: Any = Depends(get_current_group),
    common_filter_params: CommonFilterParams = Depends(CommonFilterParams),
) -> Any:
    return {"status": "ok"}


def get_app(
    *,
    add_async_safe: bool = False,
) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    if add_async_safe:
        init_app(app)

    return app
