import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.post import PostService


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
    repo.get_one_post.return_value = {"id": 1}

    result = await service.get_one_post(1)

    assert result == {"id": 1}
    repo.get_one_post.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_post(repo, service):
    payload = AsyncMock()
    repo.create_post.return_value = {"id": 1, "title": "test"}

    result = await service.create_post(payload)

    assert result == {"id": 1, "title": "test"}
    repo.create_post.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_update_post_not_found(repo, service):
    repo.get_one_post.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.update_post(1, {"title": "test"}, current_user_id=1)

    assert exc_info.value.status_code == 404
    repo.update_post.assert_not_called()


@pytest.mark.asyncio
async def test_update_post_forbidden(repo, service):
    existing_post = MagicMock(author_id=1)
    repo.get_one_post.return_value = existing_post

    with pytest.raises(HTTPException) as exc_info:
        await service.update_post(1, {"title": "test"}, current_user_id=2)

    assert exc_info.value.status_code == 403
    repo.update_post.assert_not_called()


@pytest.mark.asyncio
async def test_update_post_success(repo, service):
    payload = {"title": "new"}
    existing_post = MagicMock(author_id=1)

    repo.get_one_post.return_value = existing_post
    repo.update_post.return_value = {"id": 1, "title": "new"}

    result = await service.update_post(1, payload, current_user_id=1)

    assert result == {"id": 1, "title": "new"}
    repo.update_post.assert_called_once_with(1, payload)


@pytest.mark.asyncio
async def test_delete_post_not_found(repo, service):
    repo.get_one_post.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_post(1, current_user_id=1)

    assert exc_info.value.status_code == 404
    repo.delete_post.assert_not_called()


@pytest.mark.asyncio
async def test_delete_post_forbidden(repo, service):
    existing_post = MagicMock(author_id=1)
    repo.get_one_post.return_value = existing_post

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_post(1, current_user_id=2)

    assert exc_info.value.status_code == 403
    repo.delete_post.assert_not_called()


@pytest.mark.asyncio
async def test_delete_post_success(repo, service):
    existing_post = MagicMock(author_id=1)
    repo.get_one_post.return_value = existing_post
    repo.delete_post.return_value = True

    result = await service.delete_post(1, current_user_id=1)

    assert result is True
    repo.get_one_post.assert_called_once_with(1)
    repo.delete_post.assert_called_once_with(1)