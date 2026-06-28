import pytest
import pytest_asyncio

from sqlalchemy import select

from models.user import User
from repositories.user import UserRepository
from schemas.user import UserCreate, UserRole

@pytest_asyncio.fixture
async def repo(session):
    return UserRepository(session)

@pytest.mark.asyncio
async def test_create_user(repo, session):
    payload = UserCreate(
        username="umka",
        email="umka@mail.ru",
        role=UserRole.ADMIN,
        password_hash="123"
    )

    created_user = await repo.create_user(payload)

    result = await session.execute(
        select(User).where(User.id == created_user.id)
    )
    db_user = result.scalar_one()

    assert db_user.username == "umka"
    assert db_user.email == "umka@mail.ru"
    assert db_user.role == UserRole.ADMIN