
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
| min             | 0.45ms          | 0.12ms          | x3.60 (faster)  |
| max             | 28.60ms         | 14.28ms         | x2.00 (faster)  |
| mean            | 0.52ms          | 0.14ms          | x3.70 (faster)  |
| median          | 0.50ms          | 0.13ms          | x3.92 (faster)  |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 2.55ms          | 1.26ms          | x2.02 (faster)  |
| max             | 38.85ms         | 19.68ms         | x1.97 (faster)  |
| mean            | 6.04ms          | 1.48ms          | x4.07 (faster)  |
| median          | 5.37ms          | 1.38ms          | x3.88 (faster)  |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 7.14ms          | 3.07ms          | x2.33 (faster)  |
| max             | 48.46ms         | 28.73ms         | x1.69 (faster)  |
| mean            | 13.25ms         | 3.58ms          | x3.70 (faster)  |
| median          | 14.34ms         | 3.29ms          | x4.35 (faster)  |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 14.92ms         | 6.22ms          | x2.40 (faster)  |
| max             | 63.18ms         | 31.79ms         | x1.99 (faster)  |
| mean            | 29.80ms         | 7.71ms          | x3.86 (faster)  |
| median          | 27.70ms         | 7.16ms          | x3.87 (faster)  |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 32.16ms         | 12.21ms         | x2.63 (faster)  |
| max             | 104.02ms        | 34.68ms         | x3.00 (faster)  |
| mean            | 65.43ms         | 14.55ms         | x4.50 (faster)  |
| median          | 60.99ms         | 25.75ms         | x2.37 (faster)  |


## Concurrency 200

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 80.72ms         | 24.89ms         | x3.24 (faster)  |
| max             | 182.75ms        | 54.31ms         | x3.36 (faster)  |
| mean            | 127.81ms        | 31.01ms         | x4.12 (faster)  |
| median          | 125.15ms        | 44.50ms         | x2.81 (faster)  |

