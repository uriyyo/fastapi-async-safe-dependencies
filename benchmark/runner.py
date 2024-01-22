import time
from asyncio import gather
from dataclasses import dataclass
from enum import Enum

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from typing_extensions import Self

from benchmark.app import get_app as default_get_app
from benchmark.fastapi_example_app import get_app as fastapi_example_get_app


@dataclass
class XProcesTime:
    app: ASGIApp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        start = time.monotonic()

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["x-process-time"] = str(time.monotonic() - start)

            return await send(message)

        await self.app(scope, receive, send_wrapper)


class BenchmarkTestSuite(str, Enum):
    app = "app"
    fastapi_example = "fastapi_example"

    def __str__(self) -> str:
        return self.value


_SUITE_TO_APP = {
    BenchmarkTestSuite.app: default_get_app,
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
    runs: int,
    concurrency: int,
) -> BenchmarkResult:
    app = XProcesTime(app)

    async with (
        LifespanManager(app),
        AsyncClient(app=app, base_url="http://test.test") as client,
    ):
        times: list[float] = []

        for _ in range(runs):
            responses = await gather(*[client.get("/") for _ in range(concurrency)])
            times.extend(float(response.headers["x-process-time"]) for response in responses)

    return BenchmarkResult.from_times(times)


async def benchmark(
    *,
    runs: int,
    concurrency: int,
    suite: BenchmarkTestSuite = BenchmarkTestSuite.app,
) -> tuple[BenchmarkResult, BenchmarkResult]:
    async def _run(add_async_safe: bool) -> BenchmarkResult:
        factory = _SUITE_TO_APP[suite]

        return await benchmark_app(
            factory(add_async_safe=add_async_safe),
            runs=runs,
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
