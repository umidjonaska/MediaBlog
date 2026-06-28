import pytest
from unittest.mock import AsyncMock
from services.comment import CommentService
from fastapi import HTTPException

@pytest.fixture
def repo():
    return AsyncMock()

@pytest.fixture
def service(repo):
    return CommentService(repo)

@pytest.mark.asyncio
async def test_get_all_comment(repo, service):
    repo.get_all_comment.return_value = ['comment1', 'comment2']

    result = await service.get_all_comment()

    assert result == ['comment1', 'comment2']
    repo.get_all_comment.assert_called_once()

@pytest.mark.asyncio
async def test_get_one_comment(repo, service):
    repo.get_one_comment.return_value = {'id': 1}

    result = await service.get_one_comment(1)

    assert result == {'id': 1}
    repo.get_one_comment.assert_called_once_with(1)

@pytest.mark.asyncio
async def test_create_comment(repo, service):
    payload = AsyncMock()

    result = await service.create_comment(payload)

    assert result.status_code == 201
    repo.create_comment.assert_called_once_with(payload)

@pytest.mark.asyncio
async def test_update_comment_not_found(repo, service):
    repo.get_one_comment.return_value = None

    result = await service.update_comment(1, {'title': 'test'})
    assert result.status_code == 404

@pytest.mark.asyncio
async def test_update_comment_success(repo, service):
    payload = {'title': 'new'}

    repo.get_one_comment.return_value = {'id': 1}
    repo.update_comment.return_value = {'id': 1, 'title': 'new'}

    result = await service.update_comment(1, payload)
    assert result == {'id': 1, 'title': 'new'}
    repo.update_comment.assert_called_once_with(1, payload)

@pytest.mark.asyncio
async def test_delete_comment_success(repo, service):
    repo.get_one_comment.return_value = {"id": 1}
    repo.delete_comment.return_value = {"detail": "deleted"}

    result = await service.delete_comment(1)
    assert result == {"detail": "deleted"}

    repo.get_one_comment.assert_called_once_with(1)
    repo.delete_comment.assert_called_once_with(1)


# @pytest.mark.asyncio
# async def test_delete_post_success(repo, service):
#     repo.get_one_post.return_value = {"id": 1}
#     repo.delete_post.return_value = {"detail": "deleted"}

#     result = await service.delete_post(1)

#     assert result == {"detail": "deleted"}

#     repo.get_one_post.assert_called_once_with(1)
#     repo.delete_post.assert_called_once_with(1)

