# https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/#shortcut
from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends, FastAPI

from fastapi_async_safe import async_safe, init_app

router = APIRouter()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@async_safe
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100) -> None:
        self.q = q
        self.skip = skip
        self.limit = limit


@router.get("/")
async def read_items(commons: Annotated[CommonQueryParams, Depends()]) -> Any:
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})  # type: ignore[dict-item]
    return response


def get_app(
    *,
    add_async_safe: bool = False,
) -> FastAPI:
    app = FastAPI()
    app.include_router(router)

    if add_async_safe:
        init_app(app)

    return app
