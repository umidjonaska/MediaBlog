from typing import Any, Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    cursor: str | None = None
    next_cursor: str | None = None
    size: int
    count: int
    data: list[T]


class PageParams:
    def __init__(
        self,
        size: int,
        cursor: str | None = None,
    ):
        self.cursor = cursor
        self.size = size


def get_page_params(
    cursor: str | None = Query(
        default=None,
        description="Oxirgi element ID si. 0 yuborilsa hammasi qaytadi.",
    ),
    size: int = Query(
        default=10,
        ge=1,
        le=500,
    ),
) -> PageParams:
    return PageParams(
        size=size,
        cursor=cursor,
    )


async def pagination(
    session: AsyncSession,
    query: Select[Any],
    page_params: PageParams,
) -> Page[Any]:
    cursor = page_params.cursor
    size = page_params.size

    model = query.column_descriptions[0]["entity"]

    primary_key = next(
        col
        for col in model.__table__.columns
        if col.primary_key
    )

    # total count
    count_query = select(func.count()).select_from(model)

    if query.whereclause is not None:
        count_query = count_query.where(query.whereclause)

    total = (
        await session.execute(count_query)
    ).scalar_one()

    stmt = query.order_by(primary_key.asc())

    if cursor and cursor != "0":
        stmt = stmt.where(primary_key > int(cursor))

    if cursor != "0":
        stmt = stmt.limit(size)

    result = await session.execute(stmt)

    data = list(result.unique().scalars().all())

    next_cursor = None
    if cursor != "0" and data:
        next_cursor = str(getattr(data[-1], primary_key.name))

    return Page(
        cursor=cursor,
        next_cursor=next_cursor,
        size=size,
        count=total,
        data=data,
    )