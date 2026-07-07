import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.api import app
from app.database.database import get_db
from app.auth.services import get_current_user


@pytest_asyncio.fixture
async def client(session):
    """
    app'ga HTTP so'rov yuboradigan async client.
    get_db override qilinadi (test session bilan).
    """

    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authorized_client(client, current_user_override):
    """
    get_current_user override qilingan holatdagi client.
    current_user_override har bir test faylida (yoki test ichida) beriladi.
    """

    async def override_get_current_user():
        return current_user_override

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client