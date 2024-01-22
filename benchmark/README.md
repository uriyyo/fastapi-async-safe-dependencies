
Benchmark for simple application:
```py
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional

from fastapi import Depends, FastAPI, Query
from typing_extensions import dataclass_transform

from fastapi_async_safe import async_safe

app = FastAPI()


class DB:
    async def get(self) -> Any:
        return {"hello": "world"}


async def get_db() -> AsyncIterator[DB]:
    yield DB()


@async_safe
@dataclass_transform()
class Dependency:
    def __init_subclass__(cls, *, no_transform: bool = False, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)

        if not no_transform:
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
| min             | 0.45ms          | 0.11ms          | x3.90 faster    |
| max             | 2.26ms          | 0.32ms          | x7.02 faster    |
| mean            | 0.57ms          | 0.13ms          | x4.49 faster    |
| median          | 0.78ms          | 0.13ms          | x6.19 faster    |


## Concurrency 10

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 3.04ms          | 0.12ms          | x26.35 faster   |
| max             | 14.49ms         | 8.11ms          | x1.79 faster    |
| mean            | 5.01ms          | 0.13ms          | x38.14 faster   |
| median          | 5.38ms          | 0.12ms          | x44.01 faster   |


## Concurrency 20

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 5.42ms          | 0.11ms          | x47.93 faster   |
| max             | 21.73ms         | 8.77ms          | x2.48 faster    |
| mean            | 9.13ms          | 0.13ms          | x69.74 faster   |
| median          | 8.94ms          | 0.13ms          | x70.54 faster   |


## Concurrency 40

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 7.00ms          | 0.11ms          | x62.63 faster   |
| max             | 32.35ms         | 13.42ms         | x2.41 faster    |
| mean            | 17.46ms         | 0.13ms          | x132.60 faster  |
| median          | 19.70ms         | 0.13ms          | x145.96 faster  |


## Concurrency 50

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 14.57ms         | 0.11ms          | x128.23 faster  |
| max             | 44.44ms         | 15.30ms         | x2.90 faster    |
| mean            | 22.12ms         | 0.14ms          | x163.48 faster  |
| median          | 34.49ms         | 0.13ms          | x272.92 faster  |


## Concurrency 75

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 21.23ms         | 0.11ms          | x186.89 faster  |
| max             | 51.98ms         | 16.65ms         | x3.12 faster    |
| mean            | 33.25ms         | 0.13ms          | x246.95 faster  |
| median          | 32.53ms         | 0.21ms          | x154.01 faster  |


## Concurrency 100

| Type            | Default         | Async Safe      | Diff            |
|-----------------|-----------------|-----------------|-----------------|
| min             | 34.94ms         | 0.11ms          | x312.14 faster  |
| max             | 73.10ms         | 15.75ms         | x4.64 faster    |
| mean            | 44.32ms         | 0.13ms          | x334.91 faster  |
| median          | 47.11ms         | 0.14ms          | x338.82 faster  |

