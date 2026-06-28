import pytest

from fastapi import HTTPException
from unittest.mock import AsyncMock
from services.media import MediaService
from schemas.media import MediaStatus
from core import exception

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
    repo.get_one_media.return_value = {'id': 1}

    result = await service.get_one_media(1)
    assert result == {'id': 1}

    repo.get_one_media.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_create_media(repo, service):
    payload = AsyncMock()

    repo.create_media.return_value = 1

    result = await service.create_media(payload)
    assert result['id'] == 1
    assert result['status'] == MediaStatus.uploading

    repo.create_media.assert_called_once_with(payload)

@pytest.mark.asyncio
async def test_update_media_not_found(repo, service):
    repo.get_one_media.return_value = None

    result = await service.update_media(1, {"name": "test"})

    assert result.status_code == 404

    repo.update_media.assert_not_called()

@pytest.mark.asyncio
async def test_update_media_success(repo, service):
    payload = {'name': 'test'}

    repo.get_one_media.return_value = {"id": 1}
    repo.update_media.return_value = {"id": 1, "title": "new"}

    result = await service.update_media(1, payload)

    assert result == {"id": 1, "title": "new"}
    repo.update_media.assert_called_once_with(1, payload)

@pytest.mark.asyncio
async def test_delete_media(repo, service):
    repo.get_one_media.return_value = {"id": 1}
    repo.delete_media.return_value = {"detail": "deleted"}

    result = await service.delete_media(1)

    assert result == {"detail": "deleted"}

    repo.get_one_media.assert_called_once_with(1)
    repo.delete_media.assert_called_once_with(1)