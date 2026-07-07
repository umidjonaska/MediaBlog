import pytest
import pytest_asyncio

from fastapi import HTTPException
from sqlalchemy import select

from app.models.post import Post
from app.repositories.user import UserRepository
from app.repositories.post import PostRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.post import PostCreate, PostUpdate


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


@pytest.mark.asyncio
async def test_create_post(post_repo, author, session):
    payload = PostCreate(
        title="Birinchi post",
        content="Post matni",
        author_id=author.id,
    )

    created_post = await post_repo.create_post(payload)

    assert created_post is not None
    assert created_post.id is not None
    assert created_post.title == "Birinchi post"
    assert created_post.content == "Post matni"
    assert created_post.author_id == author.id
    assert created_post.likes == 0

    result = await session.execute(
        select(Post).where(Post.id == created_post.id)
    )
    db_post = result.scalar_one()

    assert db_post.title == "Birinchi post"


@pytest.mark.asyncio
async def test_get_one_post(post_repo, author):
    payload = PostCreate(
        title="Test post",
        content="Test content",
        author_id=author.id,
    )
    created = await post_repo.create_post(payload)

    fetched = await post_repo.get_one_post(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Test post"
    assert fetched.author.id == author.id


@pytest.mark.asyncio
async def test_get_one_post_not_found(post_repo):
    fetched = await post_repo.get_one_post(9999)

    assert fetched is None


@pytest.mark.asyncio
async def test_get_all_post(post_repo, author):
    await post_repo.create_post(PostCreate(
        title="Post 1", content="Content 1", author_id=author.id,
    ))
    await post_repo.create_post(PostCreate(
        title="Post 2", content="Content 2", author_id=author.id,
    ))

    posts = await post_repo.get_all_post()

    assert len(posts) == 2
    titles = {p.title for p in posts}
    assert titles == {"Post 1", "Post 2"}


@pytest.mark.asyncio
async def test_update_post(post_repo, author):
    created = await post_repo.create_post(PostCreate(
        title="Old title", content="Old content", author_id=author.id,
    ))

    updated = await post_repo.update_post(
        created.id,
        PostUpdate(title="New title"),
    )

    assert updated.title == "New title"
    assert updated.content == "Old content"  # o'zgarmagan


@pytest.mark.asyncio
async def test_update_post_not_found(post_repo):
    with pytest.raises(HTTPException) as exc_info:
        await post_repo.update_post(9999, PostUpdate(title="ghost"))

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_post(post_repo, author, session):
    created = await post_repo.create_post(PostCreate(
        title="To delete", content="...", author_id=author.id,
    ))

    deleted = await post_repo.delete_post(created.id)

    assert deleted is True

    result = await session.execute(
        select(Post).where(Post.id == created.id)
    )
    db_post = result.scalar_one()  # hali bazada bor

    assert db_post.is_deleted is True
    assert db_post.deleted_at is not None

    # get_one_post endi uni ko'rsatmasligi kerak
    fetched = await post_repo.get_one_post(created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_post_not_found(post_repo):
    result = await post_repo.delete_post(9999)

    assert result is None


@pytest.mark.asyncio
async def test_delete_post_already_deleted(post_repo, author):
    created = await post_repo.create_post(PostCreate(
        title="Ikki marta o'chirish", content="...", author_id=author.id,
    ))

    await post_repo.delete_post(created.id)
    second_attempt = await post_repo.delete_post(created.id)

    assert second_attempt is None