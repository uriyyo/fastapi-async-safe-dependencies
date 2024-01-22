
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
| min             | 0.45ms          | 0.12ms          | x3.64 faster    |
| max             | 19.98ms         | 15.34ms         | x1.30 faster    |
| mean            | 0.57ms          | 0.15ms          | x3.88 faster    |
| median          | 0.49ms          | 0.13ms          | x3.79 faster    |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 3.54ms          | 1.27ms          | x2.80 faster    |
| max             | 23.92ms         | 23.36ms         | x1.02 faster    |
| mean            | 6.06ms          | 1.46ms          | x4.15 faster    |
| median          | 5.33ms          | 1.38ms          | x3.85 faster    |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 6.17ms          | 3.12ms          | x1.98 faster    |
| max             | 37.60ms         | 25.79ms         | x1.46 faster    |
| mean            | 13.06ms         | 3.64ms          | x3.59 faster    |
| median          | 13.07ms         | 3.59ms          | x3.64 faster    |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 14.94ms         | 6.16ms          | x2.43 faster    |
| max             | 62.79ms         | 20.17ms         | x3.11 faster    |
| mean            | 29.69ms         | 7.17ms          | x4.14 faster    |
| median          | 33.01ms         | 6.83ms          | x4.83 faster    |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 29.73ms         | 12.51ms         | x2.38 faster    |
| max             | 97.38ms         | 39.65ms         | x2.46 faster    |
| mean            | 64.75ms         | 15.05ms         | x4.30 faster    |
| median          | 61.03ms         | 15.00ms         | x4.07 faster    |


## Concurrency 200

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 77.25ms         | 24.90ms         | x3.10 faster    |
| max             | 172.01ms        | 48.78ms         | x3.53 faster    |
| mean            | 125.36ms        | 29.78ms         | x4.21 faster    |
| median          | 124.58ms        | 28.62ms         | x4.35 faster    |

