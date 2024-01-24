# FastAPI Async Safe Dependencies

# Installation

```bash
pip install fastapi-async-safe-dependencies
```

# Introduction

FastAPI is a great framework for building APIs and the main purpose of this library is to make it a little bit better.
I guess someone (as I do) has a lot of class-based dependencies in your project.
But FastAPI comes with one little problem that will make your application slower than it could be.

Let's take a look at the following example from FastAPI documentation:

```python
from fastapi import Depends, FastAPI

app = FastAPI()

fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]

class CommonQueryParams:
    def __init__(
        self,
        q: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

This example is pretty simple and it works fine, but it has one little problem.
Whenever FastAPI tries to resolve `CommonQueryParams` dependency it will delegate object creation to
the thread-pool executor, which is not good for performance. It will happen with every request.

FastAPI logic is pretty simple, if `asyncio.iscoroutinefunction` returns `True` for the dependency, it will be called
as a simple coroutine, otherwise, it will be delegated to a thread-pool executor.

FastAPI is using `anyio.to_thread.run_sync` function to delegate object creation to the thread-pool executor.
`anyio` thread-pool executor has a limited number of threads (40 by default) which means that if you have more than 40
requests at the same time, some of them might be blocked until one of the threads from the pool is released.
Thread will be blocked by simple class instantiation, this is not CPU intensive operation,
that is not the type of task you want to delegate to the thread-pool executor.

This library provides a simple solution for this problem, that will avoid unnecessary thread-pool executor usage
for class-based dependencies and it should improve your application performance.

# Usage

Let's take a look at the same example, but with `fastapi-async-safe-dependencies` library:

```python
from fastapi import Depends, FastAPI
from fastapi_async_safe import async_safe, init_app

app = FastAPI()
init_app(app)   # don't forget to initialize application

fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]

@async_safe  # you just need to add this decorator to your dependency
class CommonQueryParams:
    def __init__(
        self,
        q: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

That's it, now your dependency will be called as simple coroutine, and it will not be delegated to the thread-pool.

Code above is equivalent to the following code:

```python
from fastapi import Depends, FastAPI

app = FastAPI()

fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]

class CommonQueryParams:
    def __init__(
        self,
        q: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit


async def _common_query_params(
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> CommonQueryParams:
    return CommonQueryParams(q=q, skip=skip, limit=limit)


@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(_common_query_params)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

# Documentation

All you need to do is to add `@async_safe` decorator to your dependency class or synchronous function that
should not be delegated to the thread-pool executor.

```python
from typing import Any
from dataclasses import dataclass

from fastapi_async_safe import async_safe

@dataclass
@async_safe
class CommonQueryParams:
    q: str | None = None
    skip: int = 0
    limit: int = 100


@async_safe
def common_query_params(
    q: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dict[str, Any]:
    return {"q": q, "skip": skip, "limit": limit}
```

Both `CommonQueryParams` class and `common_query_params` function will not be delegated to the thread-pool executor.

If your class inherits from a class that is decorated with `@async_safe` decorator then this class will be `async-safe` too.

```python
from dataclasses import dataclass

from fastapi_async_safe import async_safe

@dataclass
@async_safe
class BaseQueryParams:
    q: str | None = None


@dataclass  # this class will be async-safe too
class CommonQueryParams(BaseQueryParams):
    skip: int = 0
    limit: int = 100
```

If you don't want your inherited class to be `async-safe` you can use `@async_unsafe` decorator.

```python
from dataclasses import dataclass

from fastapi_async_safe import async_safe, async_unsafe

@dataclass
@async_safe
class BaseQueryParams:
    q: str | None = None


@dataclass
@async_unsafe  # this class no longer will be async-safe
class CommonQueryParams(BaseQueryParams):
    skip: int = 0
    limit: int = 100
```

Also, don't forget to initialize your application with `init_app` function, otherwise, `@async_safe` decorator will not
have any effect. `init_app` function will monkey-patch `Dependant` instances on application startup.

```python
from fastapi import FastAPI
from fastapi_async_safe import init_app

app = FastAPI()
init_app(app)  # don't forget to initialize application !!!
```

If you want to wrap all your class-based dependencies with `@async_safe` decorator you can pass `all_classes_safe=True`
argument to `init_app` function. It will wrap all your class-based dependencies expect those that are decorated with
`@async_unsafe` decorator.

```python
from fastapi import FastAPI
from fastapi_async_safe import init_app

app = FastAPI()
init_app(app, all_classes_safe=True)
```

# Benchmarks

Please take a look at the [benchmark](https://github.com/uriyyo/fastapi-async-safe-dependencies/tree/main/benchmark) directory for more details.

Performance boost depends on the number of class-based dependencies in your application, the more dependencies you have,
the more performance boost you will get.