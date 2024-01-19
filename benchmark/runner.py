import time
from asyncio import gather
from dataclasses import dataclass

from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send


@dataclass
class XProcesTime:
    app: ASGIApp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        start = time.monotonic_ns()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["x-process-time"] = str(time.monotonic_ns() - start)

            return await send(message)

        await self.app(scope, receive, send_wrapper)


async def benchmark(
    app: ASGIApp,
    rounds: int = 100,
    concurrency: int = 10,
) -> float:
    app = XProcesTime(app)

    async with (
        LifespanManager(app),
        AsyncClient(app=app, base_url="http://test") as client,
    ):
        times = []

        for _ in range(rounds):
            responses = await gather(*[client.get("/") for _ in range(concurrency)])
            times.extend(float(response.headers["x-process-time"]) for response in responses)

    return sum(times) / len(times)
