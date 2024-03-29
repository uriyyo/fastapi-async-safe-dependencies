from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, FastAPI, Query
from fastapi_lifespan_manager import LifespanManager
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, joinedload, mapped_column, relationship

from fastapi_async_safe import async_safe, init_app

router = APIRouter()

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@localhost:5432/benchmark",
    echo=False,
    pool_size=50,
    max_overflow=20,
    pool_timeout=30,
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class User(Base, kw_only=True):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
    name: Mapped[str] = mapped_column()
    age: Mapped[int] = mapped_column()

    marks: Mapped[list["Mark"]] = relationship(back_populates="user", default_factory=list)


class Mark(Base, kw_only=True):
    __tablename__ = "groups"

    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id), default=None)

    subject: Mapped[str] = mapped_column()
    value: Mapped[float] = mapped_column()

    user: Mapped[User] = relationship(back_populates="marks", default=None)


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )


class MarkSchema(BaseSchema):
    id: UUID

    subject: str
    value: float


class UserSchema(BaseSchema):
    id: UUID
    name: str
    age: int

    marks: list[MarkSchema]


manager = LifespanManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with engine.begin() as conn:  # noqa: SIM117
        async with AsyncSession(conn) as session:
            yield session


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        await conn.run_sync(Base.metadata.create_all)

    async with asynccontextmanager(get_db)() as session:
        session.add_all(
            [
                User(
                    name="John Doe",
                    age=20,
                    marks=[
                        Mark(subject="Math", value=5),
                        Mark(subject="Physics", value=4),
                    ],
                ),
                User(
                    name="Jane Doe",
                    age=19,
                    marks=[
                        Mark(subject="Literature", value=3),
                        Mark(subject="Music", value=4.5),
                    ],
                ),
                User(
                    name="Jack Doe",
                    age=21,
                    marks=[
                        Mark(subject="Math", value=4),
                        Mark(subject="Music", value=3.5),
                    ],
                ),
            ]
        )

        await session.commit()


@manager.add
async def on_startup() -> AsyncIterator[None]:
    await create_tables()
    yield


@async_safe
class Dependency:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        dataclass(cls)


class BaseRepository(Dependency):
    db: AsyncSession = Depends(get_db)


class UserRepository(BaseRepository):
    async def all(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
    ) -> list[User]:
        query = select(User).options(joinedload(User.marks))

        if name is not None:
            query = query.where(User.name == name)

        if age is not None:
            query = query.where(User.age == age)

        res = await self.db.scalars(query)
        return [*res.unique().all()]


class MarksRepository(BaseRepository):
    async def all(
        self,
        user_id: Optional[UUID] = None,
        subject: Optional[str] = None,
        value: Optional[float] = None,
    ) -> list[Mark]:
        query = select(Mark).options(joinedload(Mark.user))

        if user_id is not None:
            query = query.where(Mark.user_id == user_id)

        if subject is not None:
            query = query.where(Mark.subject == subject)

        if value is not None:
            query = query.where(Mark.value == value)

        res = await self.db.scalars(query)
        return [*res.unique().all()]


class UserService(Dependency):
    user_repo: UserRepository = Depends()
    marks_repo: MarksRepository = Depends()

    async def all(
        self,
        name: Optional[str] = None,
        age: Optional[int] = None,
    ) -> list[UserSchema]:
        users = await self.user_repo.all(name=name, age=age)
        return [UserSchema.model_validate(user) for user in users]


class MarksService(Dependency):
    user_repo: UserRepository = Depends()
    marks_repo: MarksRepository = Depends()

    async def all(
        self,
        user_id: Optional[UUID] = None,
        subject: Optional[str] = None,
        value: Optional[float] = None,
    ) -> list[MarkSchema]:
        marks = await self.marks_repo.all(user_id=user_id, subject=subject, value=value)
        return [MarkSchema.model_validate(mark) for mark in marks]


class UserFilterParams(Dependency):
    name: Optional[str] = Query(None, min_length=1, max_length=255)
    age: Optional[int] = Query(None, ge=0, le=100)


@router.get("/")
async def get_users(
    user_service: UserService = Depends(),
    marks_service: MarksService = Depends(),
    user_filter_params: UserFilterParams = Depends(),
) -> list[UserSchema]:
    return await user_service.all(
        name=user_filter_params.name,
        age=user_filter_params.age,
    )


def get_app(
    *,
    add_async_safe: bool = False,
) -> FastAPI:
    app = FastAPI(lifespan_manager=manager)
    app.include_router(router)

    if add_async_safe:
        init_app(app)

    return app


if __name__ == "__main__":
    # run(create_tables())

    import uvicorn

    uvicorn.run(get_app(add_async_safe=True))
