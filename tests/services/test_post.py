import pytest
from unittest.mock import AsyncMock
from services.post import PostService
from fastapi import HTTPException
from core import exception

@pytest.fixture
def repo():
    return AsyncMock()

@pytest.fixture
def service(repo):
    return PostService(repo)


@pytest.mark.asyncio
async def test_get_all_post(repo, service):
    repo.get_all_post.return_value = ["post1", "post2"]

    result = await service.get_all_post()

    assert result == ["post1", "post2"]
    repo.get_all_post.assert_called_once()

@pytest.mark.asyncio
async def test_get_one_post(repo, service):
    repo.get_one_post.return_value = {'id': 1}

    result = await service.get_one_post(1)

    assert result == {'id': 1}
    repo.get_one_post.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_post(repo, service):
    payload = AsyncMock()

    result = await service.create_post(payload)

    assert result.status_code == 201
    repo.create_post.assert_called_once_with(payload)

@pytest.mark.asyncio
async def test_update_post_not_found(repo, service):
    repo.get_one_post.return_value = None

    result = await service.update_post(1, {"name": "test"})

    assert result.status_code == 404

@pytest.mark.asyncio
async def test_update_post_success(repo, service):
    payload = {"title": "new"}

    repo.get_one_post.return_value = {"id": 1}
    repo.update_post.return_value = {"id": 1, "title": "new"}

    result = await service.update_post(1, payload)

    assert result == {"id": 1, "title": "new"}
    repo.update_post.assert_called_once_with(1, payload)

@pytest.mark.asyncio
async def test_delete_post_success(repo, service):
    repo.get_one_post.return_value = {"id": 1}
    repo.delete_post.return_value = {"detail": "deleted"}

    result = await service.delete_post(1)

    assert result == {"detail": "deleted"}

    repo.get_one_post.assert_called_once_with(1)
    repo.delete_post.assert_called_once_with(1)

