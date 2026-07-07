import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.services.comment import CommentService
from app.schemas.comment import CommentCreateIn, CommentCreate


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def service(repo):
    return CommentService(repo)


@pytest.mark.asyncio
async def test_get_all_comment(repo, service):
    repo.get_all_comment.return_value = ["comment1", "comment2"]

    result = await service.get_all_comment()

    assert result == ["comment1", "comment2"]
    repo.get_all_comment.assert_called_once()


@pytest.mark.asyncio
async def test_get_one_comment(repo, service):
    repo.get_one_comment.return_value = {"id": 1}

    result = await service.get_one_comment(1)

    assert result == {"id": 1}
    repo.get_one_comment.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_comment(repo, service):
    payload = CommentCreateIn(content="hello", post_id=1)
    repo.create_comment.return_value = {"id": 1, "content": "hello"}

    result = await service.create_comment(payload, current_user_id=5)

    assert result == {"id": 1, "content": "hello"}

    repo.create_comment.assert_called_once()
    called_arg = repo.create_comment.call_args.args[0]
    assert isinstance(called_arg, CommentCreate)
    assert called_arg.content == "hello"
    assert called_arg.post_id == 1
    assert called_arg.user_id == 5


@pytest.mark.asyncio
async def test_update_comment_not_found(repo, service):
    repo.get_one_comment.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.update_comment(1, {"content": "test"}, current_user_id=1)

    assert exc_info.value.status_code == 404
    repo.update_comment.assert_not_called()


@pytest.mark.asyncio
async def test_update_comment_forbidden(repo, service):
    existing_comment = MagicMock(user_id=1)
    repo.get_one_comment.return_value = existing_comment

    with pytest.raises(HTTPException) as exc_info:
        await service.update_comment(1, {"content": "test"}, current_user_id=2)

    assert exc_info.value.status_code == 403
    repo.update_comment.assert_not_called()


@pytest.mark.asyncio
async def test_update_comment_success(repo, service):
    payload = {"content": "new"}
    existing_comment = MagicMock(user_id=1)

    repo.get_one_comment.return_value = existing_comment
    repo.update_comment.return_value = {"id": 1, "content": "new"}

    result = await service.update_comment(1, payload, current_user_id=1)

    assert result == {"id": 1, "content": "new"}
    repo.update_comment.assert_called_once_with(1, payload)


@pytest.mark.asyncio
async def test_delete_comment_not_found(repo, service):
    repo.get_one_comment.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_comment(1, current_user_id=1)

    assert exc_info.value.status_code == 404
    repo.delete_comment.assert_not_called()


@pytest.mark.asyncio
async def test_delete_comment_forbidden(repo, service):
    existing_comment = MagicMock(user_id=1)
    repo.get_one_comment.return_value = existing_comment

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_comment(1, current_user_id=2)

    assert exc_info.value.status_code == 403
    repo.delete_comment.assert_not_called()


@pytest.mark.asyncio
async def test_delete_comment_success(repo, service):
    existing_comment = MagicMock(user_id=1)
    repo.get_one_comment.return_value = existing_comment
    repo.delete_comment.return_value = True

    result = await service.delete_comment(1, current_user_id=1)

    assert result is True
    repo.get_one_comment.assert_called_once_with(1)
    repo.delete_comment.assert_called_once_with(1)