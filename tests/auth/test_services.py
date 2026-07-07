import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.auth.services import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    authenticate_user,
    get_current_user,
    get_current_admin_user,
)
from app.schemas.user import UserRole


# ---------- PASSWORD ----------

def test_password_hash_and_verify_success():
    hashed = get_password_hash("mypassword123")

    assert hashed != "mypassword123"
    assert hashed.startswith("$argon2")
    assert verify_password("mypassword123", hashed) is True


def test_verify_password_wrong():
    hashed = get_password_hash("correctpassword")

    assert verify_password("wrongpassword", hashed) is False


# ---------- JWT ----------

@pytest.mark.asyncio
async def test_create_and_verify_access_token_roundtrip():
    token = await create_access_token({"sub": "user@mail.ru"})

    payload = await verify_token(token)

    assert payload["sub"] == "user@mail.ru"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_create_and_verify_refresh_token_roundtrip():
    token = await create_refresh_token({"sub": "user@mail.ru"})

    payload = await verify_token(token)

    assert payload["sub"] == "user@mail.ru"


@pytest.mark.asyncio
async def test_verify_token_invalid_raises_401():
    with pytest.raises(HTTPException) as exc_info:
        await verify_token("not.a.valid.token")

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_verify_token_tampered_raises_401():
    token = await create_access_token({"sub": "user@mail.ru"})
    tampered = token[:-2] + "xx"  # imzoni buzamiz

    with pytest.raises(HTTPException) as exc_info:
        await verify_token(tampered)

    assert exc_info.value.status_code == 401


# ---------- AUTHENTICATE USER ----------

@pytest.mark.asyncio
async def test_authenticate_user_success():
    db = AsyncMock()

    hashed_pw = get_password_hash("correctpassword")
    fake_user = MagicMock(username="testuser", password_hash=hashed_pw)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_user
    db.execute.return_value = result_mock

    user = await authenticate_user(db, "testuser", "correctpassword")

    assert user is fake_user


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    db = AsyncMock()

    hashed_pw = get_password_hash("correctpassword")
    fake_user = MagicMock(username="testuser", password_hash=hashed_pw)

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_user
    db.execute.return_value = result_mock

    user = await authenticate_user(db, "testuser", "wrongpassword")

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    db = AsyncMock()

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    user = await authenticate_user(db, "ghost", "anypassword")

    assert user is None


# ---------- GET CURRENT USER (Redis bilan) ----------

@pytest.mark.asyncio
async def test_get_current_user_cache_hit():
    db = AsyncMock()
    token = await create_access_token({"sub": "cached@mail.ru"})

    with patch("auth.services.RedisCLI") as mock_redis_cls:
        mock_redis = MagicMock()
        mock_redis.get.return_value = {"id": 1, "email": "cached@mail.ru", "role": "user"}
        mock_redis_cls.return_value = mock_redis

        user_data = await get_current_user(token=token, db=db)

    assert user_data["email"] == "cached@mail.ru"
    db.execute.assert_not_called()  # cache hit bo'lgani uchun DB'ga bormasligi kerak


@pytest.mark.asyncio
async def test_get_current_user_cache_miss_fetches_db():
    db = AsyncMock()
    token = await create_access_token({"sub": "fresh@mail.ru"})

    fake_user = MagicMock(id=2, email="fresh@mail.ru", role="user")
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = fake_user
    db.execute.return_value = result_mock

    with patch("auth.services.RedisCLI") as mock_redis_cls:
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis_cls.return_value = mock_redis

        user_data = await get_current_user(token=token, db=db)

    assert user_data["email"] == "fresh@mail.ru"
    mock_redis.set.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_user_not_found_in_db_raises_401():
    db = AsyncMock()
    token = await create_access_token({"sub": "ghost@mail.ru"})

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    db.execute.return_value = result_mock

    with patch("auth.services.RedisCLI") as mock_redis_cls:
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis_cls.return_value = mock_redis

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)

    assert exc_info.value.status_code == 401


# ---------- ADMIN CHECK ----------

@pytest.mark.asyncio
async def test_get_current_admin_user_forbidden_for_regular_user():
    current_user = {"id": 1, "email": "user@mail.ru", "role": UserRole.USER.value}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(current_user=current_user)

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_current_admin_user_success_for_admin():
    current_user = {"id": 1, "email": "admin@mail.ru", "role": UserRole.ADMIN.value}

    result = await get_current_admin_user(current_user=current_user)

    assert result == current_user