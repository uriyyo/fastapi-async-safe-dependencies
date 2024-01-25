import time
from asyncio import Semaphore, as_completed
from dataclasses import dataclass
from enum import Enum

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from typing_extensions import Self

from benchmark.apps.app import get_app as default_get_app
from benchmark.apps.db_app import get_app as db_get_app
from benchmark.apps.fastapi_example_app import get_app as fastapi_example_get_app
from benchmark.apps.injector import get_app as injector_get_app


@dataclass
class XProcesTime:
    app: ASGIApp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        start = time.perf_counter()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["x-process-time"] = str(time.perf_counter() - start)

            return await send(message)

        await self.app(scope, receive, send_wrapper)


class BenchmarkTestSuite(str, Enum):
    app = "app"
    db = "db"
    injector = "injector"
    fastapi_example = "fastapi_example"

    def __str__(self) -> str:
        return self.value


_SUITE_TO_APP = {
    BenchmarkTestSuite.app: default_get_app,
    BenchmarkTestSuite.db: db_get_app,
    BenchmarkTestSuite.injector: injector_get_app,
    BenchmarkTestSuite.fastapi_example: fastapi_example_get_app,
}


@dataclass
class BenchmarkResult:
    min: float
    max: float
    mean: float
    median: float

    @classmethod
    def from_times(cls, times: list[float]) -> Self:
        def _convert(t: float) -> float:  # convert to milliseconds
            return t * 1_000

        return cls(
            mean=_convert(sum(times) / len(times)),
            median=_convert(times[len(times) // 2]),
            min=_convert(min(times)),
            max=_convert(max(times)),
        )


async def benchmark_app(
    app: ASGIApp,
    *,
    requests: int,
    concurrency: int,
) -> BenchmarkResult:
    app = XProcesTime(app)

    semaphore = Semaphore(concurrency)

    async with (
        LifespanManager(app),
        AsyncClient(app=app, base_url="http://test.test") as client,
    ):
        times: list[float] = []

        async def _run() -> float:
            async with semaphore:
                response = await client.get("/")
                response.raise_for_status()

            return float(response.headers["x-process-time"])

        for f in as_completed([_run() for _ in range(requests)]):
            times.append(await f)

    return BenchmarkResult.from_times(times)


async def benchmark(
    *,
    requests: int,
    concurrency: int,
    suite: BenchmarkTestSuite = BenchmarkTestSuite.app,
) -> tuple[BenchmarkResult, BenchmarkResult]:
    async def _run(add_async_safe: bool) -> BenchmarkResult:
        factory = _SUITE_TO_APP[suite]

        return await benchmark_app(
            factory(add_async_safe=add_async_safe),
            requests=requests,
            concurrency=concurrency,
        )

    default_run = await _run(False)
    async_safe_run = await _run(True)

    return default_run, async_safe_run


__all__ = [
    "BenchmarkTestSuite",
    "BenchmarkResult",
    "benchmark",
]
