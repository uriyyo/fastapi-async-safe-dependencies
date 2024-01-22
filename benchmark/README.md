
Benchmark for simple application:
```py
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

from fastapi import Depends, FastAPI, Query

from fastapi_async_safe import async_safe

app = FastAPI()


class DB:
    async def get(self) -> Any:
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


@app.get("/")
async def get_users(
    current_user: Any = Depends(get_current_user),
    current_group: Any = Depends(get_current_group),
    common_filter_params: CommonFilterParams = Depends(CommonFilterParams),
) -> Any:
    return {"status": "ok"}
```


## Concurrency 1

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 0.47ms          | 0.12ms          | x3.99 faster    |
| max             | 2.12ms          | 0.35ms          | x6.06 faster    |
| mean            | 0.54ms          | 0.13ms          | x4.13 faster    |
| median          | 0.52ms          | 0.12ms          | x4.37 faster    |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 3.07ms          | 0.11ms          | x26.78 faster   |
| max             | 13.27ms         | 0.75ms          | x17.58 faster   |
| mean            | 4.92ms          | 0.13ms          | x37.47 faster   |
| median          | 4.63ms          | 0.12ms          | x37.45 faster   |


## Concurrency 25

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 6.33ms          | 0.11ms          | x55.41 faster   |
| max             | 22.29ms         | 9.80ms          | x2.27 faster    |
| mean            | 11.19ms         | 0.13ms          | x84.11 faster   |
| median          | 12.97ms         | 0.13ms          | x100.67 faster  |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 14.05ms         | 0.11ms          | x124.44 faster  |
| max             | 38.83ms         | 14.45ms         | x2.69 faster    |
| mean            | 22.20ms         | 0.14ms          | x162.68 faster  |
| median          | 24.21ms         | 0.13ms          | x190.19 faster  |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 35.97ms         | 0.11ms          | x317.66 faster  |
| max             | 67.41ms         | 15.72ms         | x4.29 faster    |
| mean            | 44.57ms         | 0.13ms          | x335.25 faster  |
| median          | 41.44ms         | 0.13ms          | x323.34 faster  |

