
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
| min             | 0.70ms          | 0.28ms          | x2.48 (faster)  |
| max             | 70.22ms         | 22.66ms         | x3.10 (faster)  |
| mean            | 0.79ms          | 0.31ms          | x2.54 (faster)  |
| median          | 0.74ms          | 0.29ms          | x2.54 (faster)  |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 0.92ms          | 2.77ms          | x0.33 (slower)  |
| max             | 64.83ms         | 53.82ms         | x1.20 (faster)  |
| mean            | 10.20ms         | 3.03ms          | x3.37 (faster)  |
| median          | 6.07ms          | 2.91ms          | x2.09 (faster)  |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 0.93ms          | 6.92ms          | x0.13 (slower)  |
| max             | 84.35ms         | 58.98ms         | x1.43 (faster)  |
| mean            | 23.19ms         | 7.48ms          | x3.10 (faster)  |
| median          | 25.95ms         | 28.77ms         | x0.90 (slower)  |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 21.97ms         | 13.80ms         | x1.59 (faster)  |
| max             | 111.00ms        | 57.10ms         | x1.94 (faster)  |
| mean            | 47.37ms         | 15.45ms         | x3.07 (faster)  |
| median          | 48.87ms         | 15.07ms         | x3.24 (faster)  |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 45.29ms         | 26.93ms         | x1.68 (faster)  |
| max             | 149.68ms        | 63.19ms         | x2.37 (faster)  |
| mean            | 98.99ms         | 30.44ms         | x3.25 (faster)  |
| median          | 121.55ms        | 29.50ms         | x4.12 (faster)  |


## Concurrency 200

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 99.30ms         | 54.44ms         | x1.82 (faster)  |
| max             | 275.28ms        | 106.27ms        | x2.59 (faster)  |
| mean            | 202.16ms        | 61.14ms         | x3.31 (faster)  |
| median          | 204.80ms        | 59.63ms         | x3.43 (faster)  |

