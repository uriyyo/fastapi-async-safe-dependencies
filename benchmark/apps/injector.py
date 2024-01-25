from dataclasses import dataclass
from typing import Any

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, FastAPI

from fastapi_async_safe import async_safe, init_app


class DB:
    async def get(self) -> Any:
        return {"hello": "world"}


@async_safe
class Dependency:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        dataclass(cls)


class UserRepository(Dependency):
    db: DB

    async def get(self) -> Any:
        return await self.db.get()


class GroupRepository(Dependency):
    db: DB

    async def get(self) -> Any:
        return await self.db.get()


class UserService(Dependency):
    user_repo: UserRepository

    async def get(self) -> Any:
        return await self.user_repo.get()


class GroupService(Dependency):
    group_repo: GroupRepository

    async def get(self) -> Any:
        return await self.group_repo.get()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[__name__])

    db = providers.Factory(DB)

    user_repo = providers.Factory(UserRepository, db=db)
    group_repo = providers.Factory(GroupRepository, db=db)

    user_service = providers.Factory(UserService, user_repo=user_repo)
    group_service = providers.Factory(GroupService, group_repo=group_repo)


router = APIRouter()


@router.get("/")
@inject
async def index(
    group_service: GroupService = Depends(Provide[Container.group_service]),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> dict[str, Any]:
    return {}


def get_app(
    *,
    add_async_safe: bool = False,
) -> FastAPI:
    container = Container()

    app = FastAPI()
    app.container = container  # type: ignore[attr-defined]
    app.include_router(router)

    if add_async_safe:
        init_app(app)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(get_app(add_async_safe=True))
