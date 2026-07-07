import pytest
import pytest_asyncio

from typing import Any

from sqlalchemy import select

from app.models.media import Media
from app.repositories.user import UserRepository
from app.repositories.media import MediaRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.media import MediaCreate, MediaUpdate, MediaType, MediaStatus
from app.utils.pagination import PageParams


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


def make_media_payload(owner_id: int, **overrides: Any) -> MediaCreate:
    data: dict[str, Any] = dict(
        filename="video.mp4",
        path="/media/video.mp4",
        mime_type="video/mp4",
        type=MediaType.video,
        size=1024,
        owner_id=owner_id,
    )
    data.update(overrides)
    return MediaCreate(**data)


@pytest.mark.asyncio
async def test_create_media(media_repo, owner, session):
    payload = make_media_payload(owner.id)

    media_id = await media_repo.create_media(payload)

    assert media_id is not None

    result = await session.execute(select(Media).where(Media.id == media_id))
    db_media = result.scalar_one()

    assert db_media.filename == "video.mp4"
    assert db_media.owner_id == owner.id
    assert db_media.status == MediaStatus.uploading


@pytest.mark.asyncio
async def test_get_one_media(media_repo, owner):
    payload = make_media_payload(owner.id, filename="image.png", type=MediaType.image)
    media_id = await media_repo.create_media(payload)

    fetched = await media_repo.get_one_media(media_id)

    assert fetched is not None
    assert fetched.id == media_id
    assert fetched.filename == "image.png"
    assert fetched.owner.id == owner.id


@pytest.mark.asyncio
async def test_get_one_media_not_found(media_repo):
    fetched = await media_repo.get_one_media(9999)

    assert fetched is None


@pytest.mark.asyncio
async def test_get_all_media_excludes_deleted(media_repo, owner):
    await media_repo.create_media(make_media_payload(owner.id, filename="a.mp4"))
    id2 = await media_repo.create_media(make_media_payload(owner.id, filename="b.mp4"))

    # b.mp4 statusini "deleted" qilib belgilaymiz
    await media_repo.update_media(id2, MediaUpdate(status=MediaStatus.deleted))

    page_params = PageParams(size=10)
    result = await media_repo.get_all_media(page_params)

    filenames = {item.filename for item in result.data}

    assert "a.mp4" in filenames
    assert "b.mp4" not in filenames


@pytest.mark.asyncio
async def test_update_media(media_repo, owner):
    media_id = await media_repo.create_media(make_media_payload(owner.id))

    updated = await media_repo.update_media(
        media_id,
        MediaUpdate(status=MediaStatus.uploaded, resolution="1920x1080"),
    )

    assert updated.status == MediaStatus.uploaded
    assert updated.resolution == "1920x1080"
    assert updated.filename == "video.mp4"  # o'zgarmagan


@pytest.mark.asyncio
async def test_update_media_not_found(media_repo):
    with pytest.raises(Exception):  # HTTPException 404
        await media_repo.update_media(9999, MediaUpdate(status=MediaStatus.failed))


@pytest.mark.asyncio
async def test_delete_media(media_repo, owner, session):
    media_id = await media_repo.create_media(make_media_payload(owner.id))

    deleted = await media_repo.delete_media(media_id)

    assert deleted is True

    result = await session.execute(select(Media).where(Media.id == media_id))
    db_media = result.scalar_one()

    # soft delete: yozuv bazada qoladi, faqat status/deleted_at o'zgaradi
    assert db_media.status == MediaStatus.deleted
    assert db_media.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_media_not_found(media_repo):
    result = await media_repo.delete_media(9999)

    assert result is None