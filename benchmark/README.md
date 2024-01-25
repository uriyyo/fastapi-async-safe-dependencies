
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
| min             | 0.46ms          | 0.12ms          | x3.69 (faster)  |
| max             | 30.19ms         | 23.32ms         | x1.29 (faster)  |
| mean            | 0.53ms          | 0.15ms          | x3.65 (faster)  |
| median          | 0.51ms          | 0.14ms          | x3.66 (faster)  |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 3.63ms          | 1.24ms          | x2.93 (faster)  |
| max             | 54.87ms         | 17.87ms         | x3.07 (faster)  |
| mean            | 6.32ms          | 1.49ms          | x4.23 (faster)  |
| median          | 7.11ms          | 1.37ms          | x5.19 (faster)  |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 7.85ms          | 3.08ms          | x2.54 (faster)  |
| max             | 53.04ms         | 34.97ms         | x1.52 (faster)  |
| mean            | 13.66ms         | 3.65ms          | x3.74 (faster)  |
| median          | 13.10ms         | 3.40ms          | x3.85 (faster)  |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 13.84ms         | 6.07ms          | x2.28 (faster)  |
| max             | 65.13ms         | 32.73ms         | x1.99 (faster)  |
| mean            | 30.14ms         | 7.61ms          | x3.96 (faster)  |
| median          | 31.49ms         | 6.71ms          | x4.69 (faster)  |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 26.92ms         | 12.23ms         | x2.20 (faster)  |
| max             | 110.42ms        | 41.18ms         | x2.68 (faster)  |
| mean            | 66.53ms         | 15.24ms         | x4.37 (faster)  |
| median          | 64.78ms         | 14.68ms         | x4.41 (faster)  |


## Concurrency 200

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 62.08ms         | 24.76ms         | x2.51 (faster)  |
| max             | 203.59ms        | 55.03ms         | x3.70 (faster)  |
| mean            | 132.10ms        | 31.52ms         | x4.19 (faster)  |
| median          | 133.36ms        | 47.89ms         | x2.78 (faster)  |

