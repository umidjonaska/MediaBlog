import sys
import os

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from api import app

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

from database.database import Base

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def client():
    """
    Barcha testlar uchun bitta TestClient
    """
    return TestClient(app)

DATABASE_URL = (
    "postgresql+asyncpg://postgres:1234@127.0.0.1/media_blog_test"
)

engine = create_async_engine(DATABASE_URL)

TestingSession = async_sessionmaker(
    engine,
    expire_on_commit=False
)

@pytest_asyncio.fixture
async def session():

    async with TestingSession() as session:
        result = await session.execute(text("SELECT current_database()"))
        print("TEST DB:", result.scalar())

        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSession() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)