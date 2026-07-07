import pytest
import pytest_asyncio
import io

from app.repositories.user import UserRepository
from app.repositories.media import MediaRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.media import MediaCreate, MediaType, MediaStatus, MediaUpdate


@pytest_asyncio.fixture
async def user_repo(session):
    return UserRepository(session)


@pytest_asyncio.fixture
async def media_repo(session):
    return MediaRepository(session)


@pytest_asyncio.fixture
async def owner(user_repo):
    payload = UserCreate(
        username="owner1",
        email="owner1@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def other_user(user_repo):
    payload = UserCreate(
        username="otheruser",
        email="other@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def existing_media(media_repo, owner):
    payload = MediaCreate(
        filename="video.mp4",
        path="/media/video.mp4",
        mime_type="video/mp4",
        type=MediaType.video,
        size=1024,
        owner_id=owner.id,
    )
    media_id = await media_repo.create_media(payload)
    return await media_repo.get_one_media(media_id)


@pytest_asyncio.fixture
async def current_user_override(owner):
    return {
        "id": owner.id,
        "email": owner.email,
        "role": owner.role.value,
    }


@pytest.mark.asyncio
async def test_get_all_media_requires_auth(client):
    response = await client.get("/media")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_media_with_auth(authorized_client, existing_media):
    response = await authorized_client.get("/media")

    assert response.status_code == 200
    data = response.json()
    filenames = {item["filename"] for item in data["data"]}
    assert "video.mp4" in filenames


@pytest.mark.asyncio
async def test_get_one_media(authorized_client, existing_media):
    response = await authorized_client.get(f"/media/{existing_media.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == existing_media.id
    assert data["filename"] == "video.mp4"


@pytest.mark.asyncio
async def test_get_one_media_not_found(authorized_client):
    response = await authorized_client.get("/media/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_own_media(authorized_client, existing_media):
    response = await authorized_client.put(
        f"/media/{existing_media.id}",
        json={"resolution": "1920x1080"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resolution"] == "1920x1080"


@pytest.mark.asyncio
async def test_update_media_not_found(authorized_client):
    response = await authorized_client.put(
        "/media/9999",
        json={"resolution": "1920x1080"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_others_media_forbidden(client, existing_media, other_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": other_user.id, "email": other_user.email, "role": other_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.put(
        f"/media/{existing_media.id}",
        json={"resolution": "666x666"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_own_media(authorized_client, existing_media, session):
    from sqlalchemy import select
    from app.models.media import Media

    response = await authorized_client.delete(f"/media/{existing_media.id}")

    assert response.status_code == 200

    result = await session.execute(select(Media).where(Media.id == existing_media.id))
    db_media = result.scalar_one()

    assert db_media.status == MediaStatus.deleted
    assert db_media.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_media_not_found(authorized_client):
    response = await authorized_client.delete("/media/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_others_media_forbidden(client, existing_media, other_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": other_user.id, "email": other_user.email, "role": other_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.delete(f"/media/{existing_media.id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_upload_media(authorized_client, owner, monkeypatch, session):
    async def fake_save_file(file, media_type):
        return "fake_video.mp4", "/media/fake_video.mp4", 2048

    async def fake_process_media(media_id, path, media_type):
        return None

    monkeypatch.setattr("services.media.save_file", fake_save_file)
    monkeypatch.setattr("services.media.process_media", fake_process_media)
    monkeypatch.setattr("services.media.detect_media_type", lambda content_type: MediaType.video)

    file_content = b"fake video bytes"
    files = {"file": ("test.mp4", io.BytesIO(file_content), "video/mp4")}

    response = await authorized_client.post("/media/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploading"
    assert "id" in data


@pytest.mark.asyncio
async def test_upload_media_requires_auth(client):
    file_content = b"fake video bytes"
    files = {"file": ("test.mp4", io.BytesIO(file_content), "video/mp4")}

    response = await client.post("/media/upload", files=files)

    assert response.status_code == 401