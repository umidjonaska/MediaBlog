import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.media import MediaService
from app.schemas.media import MediaStatus


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def service(repo):
    return MediaService(repo)


@pytest.mark.asyncio
async def test_get_all_media(repo, service):
    repo.get_all_media.return_value = ["media1", "media2"]

    result = await service.get_all_media(1)

    assert result == ["media1", "media2"]
    repo.get_all_media.assert_called_once()


@pytest.mark.asyncio
async def test_get_one_media(repo, service):
    repo.get_one_media.return_value = {"id": 1}

    result = await service.get_one_media(1)

    assert result == {"id": 1}
    repo.get_one_media.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_media(repo, service):
    payload = AsyncMock()
    repo.create_media.return_value = 1

    result = await service.create_media(payload)

    assert result["id"] == 1
    assert result["status"] == MediaStatus.uploading
    repo.create_media.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_update_media_not_found(repo, service):
    repo.get_one_media.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.update_media(1, {"resolution": "test"}, current_user_id=1)

    assert exc_info.value.status_code == 404
    repo.update_media.assert_not_called()


@pytest.mark.asyncio
async def test_update_media_forbidden(repo, service):
    existing_media = MagicMock(owner_id=1)
    repo.get_one_media.return_value = existing_media

    with pytest.raises(HTTPException) as exc_info:
        await service.update_media(1, {"resolution": "test"}, current_user_id=2)

    assert exc_info.value.status_code == 403
    repo.update_media.assert_not_called()


@pytest.mark.asyncio
async def test_update_media_success(repo, service):
    payload = {"resolution": "test"}
    existing_media = MagicMock(owner_id=1)

    repo.get_one_media.return_value = existing_media
    repo.update_media.return_value = {"id": 1, "resolution": "test"}

    result = await service.update_media(1, payload, current_user_id=1)

    assert result == {"id": 1, "resolution": "test"}
    repo.update_media.assert_called_once_with(1, payload)


@pytest.mark.asyncio
async def test_delete_media_not_found(repo, service):
    repo.get_one_media.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_media(1, current_user_id=1)

    assert exc_info.value.status_code == 404
    repo.delete_media.assert_not_called()


@pytest.mark.asyncio
async def test_delete_media_forbidden(repo, service):
    existing_media = MagicMock(owner_id=1)
    repo.get_one_media.return_value = existing_media

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_media(1, current_user_id=2)

    assert exc_info.value.status_code == 403
    repo.delete_media.assert_not_called()


@pytest.mark.asyncio
async def test_delete_media_success(repo, service):
    existing_media = MagicMock(owner_id=1)
    repo.get_one_media.return_value = existing_media
    repo.delete_media.return_value = True

    result = await service.delete_media(1, current_user_id=1)

    assert result is True
    repo.get_one_media.assert_called_once_with(1)
    repo.delete_media.assert_called_once_with(1)