
Benchmark for simple application:
```py
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
```


## Concurrency 1

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 0.69ms          | 0.28ms          | x2.45 faster    |
| max             | 50.86ms         | 21.28ms         | x2.39 faster    |
| mean            | 0.80ms          | 0.30ms          | x2.67 faster    |
| median          | 0.83ms          | 0.29ms          | x2.89 faster    |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 0.92ms          | 2.78ms          | x0.33 faster    |
| max             | 63.80ms         | 32.85ms         | x1.94 faster    |
| mean            | 10.13ms         | 3.02ms          | x3.36 faster    |
| median          | 6.61ms          | 2.95ms          | x2.24 faster    |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 0.92ms          | 6.87ms          | x0.13 faster    |
| max             | 81.92ms         | 57.07ms         | x1.44 faster    |
| mean            | 22.60ms         | 7.48ms          | x3.02 faster    |
| median          | 18.54ms         | 7.49ms          | x2.48 faster    |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 19.27ms         | 13.73ms         | x1.40 faster    |
| max             | 113.67ms        | 57.82ms         | x1.97 faster    |
| mean            | 46.61ms         | 15.45ms         | x3.02 faster    |
| median          | 43.83ms         | 15.09ms         | x2.90 faster    |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 43.50ms         | 28.08ms         | x1.55 faster    |
| max             | 177.17ms        | 85.17ms         | x2.08 faster    |
| mean            | 103.24ms        | 32.88ms         | x3.14 faster    |
| median          | 134.49ms        | 31.24ms         | x4.31 faster    |


## Concurrency 200

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 114.19ms        | 54.72ms         | x2.09 faster    |
| max             | 299.55ms        | 122.07ms        | x2.45 faster    |
| mean            | 210.90ms        | 61.94ms         | x3.40 faster    |
| median          | 206.49ms        | 60.11ms         | x3.44 faster    |

