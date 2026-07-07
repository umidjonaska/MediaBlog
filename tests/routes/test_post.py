import pytest
import pytest_asyncio

from app.repositories.user import UserRepository
from app.repositories.post import PostRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.post import PostCreate


@pytest_asyncio.fixture
async def user_repo(session):
    return UserRepository(session)


@pytest_asyncio.fixture
async def post_repo(session):
    return PostRepository(session)


@pytest_asyncio.fixture
async def author(user_repo):
    payload = UserCreate(
        username="author1",
        email="author1@mail.ru",
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
async def existing_post(post_repo, author):
    return await post_repo.create_post(PostCreate(
        title="Existing post",
        content="Some content",
        author_id=author.id,
    ))


@pytest_asyncio.fixture
async def current_user_override(author):
    return {
        "id": author.id,
        "email": author.email,
        "role": author.role.value,
    }


@pytest.mark.asyncio
async def test_get_all_posts_requires_auth(client):
    response = await client.get("/post")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_posts_with_auth(authorized_client, existing_post):
    response = await authorized_client.get("/post")

    assert response.status_code == 200
    data = response.json()
    titles = {item["title"] for item in data["data"]}
    assert "Existing post" in titles


@pytest.mark.asyncio
async def test_get_one_post(authorized_client, existing_post):
    response = await authorized_client.get(f"/post/{existing_post.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == existing_post.id
    assert data["title"] == "Existing post"


@pytest.mark.asyncio
async def test_get_one_post_not_found(authorized_client):
    response = await authorized_client.get("/post/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_post_binds_current_user_as_author(authorized_client, author):
    response = await authorized_client.post(
        "/post",
        json={"title": "New post", "content": "New content"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New post"
    assert data["author_id"] == author.id


@pytest.mark.asyncio
async def test_update_own_post(authorized_client, existing_post):
    response = await authorized_client.put(
        f"/post/{existing_post.id}",
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"


@pytest.mark.asyncio
async def test_update_post_not_found(authorized_client):
    response = await authorized_client.put(
        "/post/9999",
        json={"title": "ghost"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_others_post_forbidden(client, existing_post, other_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": other_user.id, "email": other_user.email, "role": other_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.put(
        f"/post/{existing_post.id}",
        json={"title": "Hijacked title"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_own_post(authorized_client, existing_post, session):
    from sqlalchemy import select
    from app.models.post import Post

    response = await authorized_client.delete(f"/post/{existing_post.id}")

    assert response.status_code == 200

    result = await session.execute(select(Post).where(Post.id == existing_post.id))
    db_post = result.scalar_one()

    assert db_post.is_deleted is True


@pytest.mark.asyncio
async def test_delete_post_not_found(authorized_client):
    response = await authorized_client.delete("/post/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_others_post_forbidden(client, existing_post, other_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": other_user.id, "email": other_user.email, "role": other_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user

    response = await client.delete(f"/post/{existing_post.id}")

    assert response.status_code == 403