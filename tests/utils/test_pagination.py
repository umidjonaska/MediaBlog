import pytest
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserRole
from app.utils.pagination import pagination, PageParams
from app.auth.services import get_password_hash


async def _create_user(session, username: str, email: str) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=get_password_hash("pass123"),
        role=UserRole.USER,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_pagination_default_cursor_applies_limit(session):
    """
    cursor berilmasa (None), limit qo'llanishi kerak (birinchi sahifa)
    """
    for i in range(5):
        await _create_user(session, f"user{i}", f"user{i}@mail.ru")

    query = select(User)
    page_params = PageParams(size=2)  # cursor=None

    page = await pagination(session, query, page_params)

    assert page.count == 5
    assert len(page.data) == 2
    assert page.next_cursor is not None


@pytest.mark.asyncio
async def test_pagination_cursor_zero_returns_all(session):
    """
    cursor="0" bo'lsa, limit qo'llanmasligi va hammasi qaytishi kerak
    """
    for i in range(5):
        await _create_user(session, f"user{i}", f"user{i}@mail.ru")

    query = select(User)
    page_params = PageParams(size=2, cursor="0")

    page = await pagination(session, query, page_params)

    assert page.count == 5
    assert len(page.data) == 5
    assert page.next_cursor is None


@pytest.mark.asyncio
async def test_pagination_next_page_using_cursor(session):
    """
    next_cursor orqali ikkinchi sahifaga o'tish, natijalar takrorlanmasligi kerak
    """
    users = []
    for i in range(5):
        users.append(await _create_user(session, f"user{i}", f"user{i}@mail.ru"))

    query = select(User)

    first_page = await pagination(session, query, PageParams(size=2))
    assert len(first_page.data) == 2
    first_ids = [u.id for u in first_page.data]

    second_page = await pagination(
        session, query, PageParams(size=2, cursor=first_page.next_cursor)
    )
    second_ids = [u.id for u in second_page.data]

    assert all(sid > first_ids[-1] for sid in second_ids)
    assert set(first_ids).isdisjoint(set(second_ids))


@pytest.mark.asyncio
async def test_pagination_last_page_has_no_next_cursor_issue(session):
    """
    Oxirgi sahifada data kam bo'lsa ham, next_cursor hisoblanadi
    (bu funksiya "hasNextPage" ni bilmaydi, shuni hujjatlashtiramiz)
    """
    for i in range(3):
        await _create_user(session, f"lastpage{i}", f"lastpage{i}@mail.ru")

    query = select(User)
    page_params = PageParams(size=10)  # size jami elementlardan katta

    page = await pagination(session, query, page_params)

    assert len(page.data) == 3
    assert page.count == 3
    # Diqqat: next_cursor baribir set qilinadi, chunki funksiya
    # "bu oxirgi sahifami" tekshirmaydi - shuni bilib qo'yish kerak
    assert page.next_cursor is not None


@pytest.mark.asyncio
async def test_pagination_empty_result(session):
    query = select(User)
    page_params = PageParams(size=10)

    page = await pagination(session, query, page_params)

    assert page.count == 0
    assert page.data == []
    assert page.next_cursor is None


@pytest.mark.asyncio
async def test_pagination_respects_where_clause(session):
    """
    query'ga qo'shilgan .where() filtri count'ga ham, data'ga ham ta'sir qilishi kerak
    """
    await _create_user(session, "alice", "alice@mail.ru")
    await _create_user(session, "bob", "bob@mail.ru")

    query = select(User).where(User.username == "alice")
    page_params = PageParams(size=10, cursor="0")

    page = await pagination(session, query, page_params)

    assert page.count == 1
    assert len(page.data) == 1
    assert page.data[0].username == "alice"


@pytest.mark.asyncio
async def test_pagination_orders_by_primary_key(session):
    for i in range(3):
        await _create_user(session, f"orderuser{i}", f"orderuser{i}@mail.ru")

    query = select(User)
    page_params = PageParams(size=10, cursor="0")

    page = await pagination(session, query, page_params)

    ids = [u.id for u in page.data]
    assert ids == sorted(ids)


@pytest.mark.asyncio
async def test_pagination_size_field_reflects_input(session):
    await _create_user(session, "sizetest", "sizetest@mail.ru")

    query = select(User)
    page_params = PageParams(size=7, cursor="0")

    page = await pagination(session, query, page_params)

    assert page.size == 7