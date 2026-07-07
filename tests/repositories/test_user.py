import pytest
import pytest_asyncio

from fastapi import HTTPException
from sqlalchemy import select

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserRole


@pytest_asyncio.fixture
async def repo(session):
    return UserRepository(session)


@pytest.mark.asyncio
async def test_create_user(repo, session):
    payload = UserCreate(
        username="umka",
        email="umka@mail.ru",
        role=UserRole.ADMIN,
        password_hash="123",
    )

    created_user = await repo.create_user(payload)

    assert created_user.username == "umka"
    assert created_user.email == "umka@mail.ru"
    assert created_user.role == UserRole.ADMIN

    result = await session.execute(
        select(User).where(User.id == created_user.id)
    )
    db_user = result.scalar_one()

    assert db_user.username == "umka"
    assert db_user.email == "umka@mail.ru"
    assert db_user.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_get_one_user(repo):
    payload = UserCreate(
        username="umka",
        email="umka@mail.ru",
        role=UserRole.ADMIN,
        password_hash="123",
    )
    created_user = await repo.create_user(payload)

    fetched = await repo.get_one_user(created_user.id)

    assert fetched is not None
    assert fetched.id == created_user.id
    assert fetched.username == "umka"


@pytest.mark.asyncio
async def test_get_one_user_not_found(repo):
    fetched = await repo.get_one_user(9999)

    assert fetched is None


@pytest.mark.asyncio
async def test_get_all_user(repo):
    await repo.create_user(UserCreate(
        username="user1",
        email="user1@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    ))
    await repo.create_user(UserCreate(
        username="user2",
        email="user2@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    ))

    users = await repo.get_all_user()

    assert len(users) == 2
    usernames = {u.username for u in users}
    assert usernames == {"user1", "user2"}


@pytest.mark.asyncio
async def test_update_user(repo):
    created_user = await repo.create_user(UserCreate(
        username="old_name",
        email="old@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    ))

    updated = await repo.update_user(
        created_user.id,
        UserUpdate(username="new_name"),
    )

    assert updated.username == "new_name"
    assert updated.email == "old@mail.ru"


@pytest.mark.asyncio
async def test_update_user_not_found(repo):
    with pytest.raises(HTTPException) as exc_info:
        await repo.update_user(9999, UserUpdate(username="ghost"))

    assert exc_info.value.status_code == 404