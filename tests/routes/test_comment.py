import pytest
import pytest_asyncio

from app.repositories.user import UserRepository
from app.repositories.post import PostRepository
from app.repositories.comment import CommentRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.post import PostCreate


@pytest_asyncio.fixture
async def user_repo(session):
    return UserRepository(session)


@pytest_asyncio.fixture
async def post_repo(session):
    return PostRepository(session)


@pytest_asyncio.fixture
async def comment_repo(session):
    return CommentRepository(session)


@pytest_asyncio.fixture
async def author(user_repo):
    payload = UserCreate(
        username="author1", email="author1@mail.ru",
        role=UserRole.USER, password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def commenter(user_repo):
    payload = UserCreate(
        username="commenter1", email="commenter1@mail.ru",
        role=UserRole.USER, password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def other_user(user_repo):
    payload = UserCreate(
        username="otheruser", email="other@mail.ru",
        role=UserRole.USER, password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def post(post_repo, author):
    return await post_repo.create_post(PostCreate(
        title="Test post", content="Test content", author_id=author.id,
    ))


@pytest_asyncio.fixture
async def existing_comment(comment_repo, commenter, post):
    from app.schemas.comment import CommentCreate
    return await comment_repo.create_comment(CommentCreate(
        content="Existing comment", user_id=commenter.id, post_id=post.id,
    ))


@pytest_asyncio.fixture
async def current_user_override(commenter):
    return {
        "id": commenter.id,
        "email": commenter.email,
        "role": commenter.role.value,
    }


@pytest.mark.asyncio
async def test_get_all_comments_requires_auth(client):
    response = await client.get("/comment")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_comments_with_auth(authorized_client, existing_comment):
    response = await authorized_client.get("/comment")

    assert response.status_code == 200
    data = response.json()
    contents = {item["content"] for item in data["data"]}
    assert "Existing comment" in contents


@pytest.mark.asyncio
async def test_get_one_comment(authorized_client, existing_comment):
    response = await authorized_client.get(f"/comment/{existing_comment.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == existing_comment.id
    assert data["content"] == "Existing comment"


@pytest.mark.asyncio
async def test_get_one_comment_not_found(authorized_client):
    response = await authorized_client.get("/comment/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_comment_binds_current_user(authorized_client, commenter, post):
    response = await authorized_client.post(
        "/comment",
        json={"content": "New comment", "post_id": post.id},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "New comment"
    assert data["user_id"] == commenter.id
    assert data["post_id"] == post.id


@pytest.mark.asyncio
async def test_update_own_comment(authorized_client, existing_comment):
    response = await authorized_client.put(
        f"/comment/{existing_comment.id}",
        json={"content": "Updated content"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated content"


@pytest.mark.asyncio
async def test_update_comment_not_found(authorized_client):
    response = await authorized_client.put(
        "/comment/9999",
        json={"content": "ghost"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_others_comment_forbidden(client, existing_comment, other_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": other_user.id, "email": other_user.email, "role": other_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.put(
        f"/comment/{existing_comment.id}",
        json={"content": "Hijacked"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_own_comment(authorized_client, existing_comment, session):
    from sqlalchemy import select
    from app.models.comment import Comment

    response = await authorized_client.delete(f"/comment/{existing_comment.id}")

    assert response.status_code == 200

    result = await session.execute(select(Comment).where(Comment.id == existing_comment.id))
    db_comment = result.scalar_one()

    assert db_comment.is_deleted is True


@pytest.mark.asyncio
async def test_delete_comment_not_found(authorized_client):
    response = await authorized_client.delete("/comment/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_others_comment_forbidden(client, existing_comment, other_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": other_user.id, "email": other_user.email, "role": other_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.delete(f"/comment/{existing_comment.id}")

    assert response.status_code == 403