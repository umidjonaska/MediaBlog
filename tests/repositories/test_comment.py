import pytest
import pytest_asyncio

from sqlalchemy import select

from app.models.comment import Comment
from app.repositories.user import UserRepository
from app.repositories.post import PostRepository
from app.repositories.comment import CommentRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.post import PostCreate
from app.schemas.comment import CommentCreate, CommentUpdate


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
        username="author1",
        email="author1@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def commenter(user_repo):
    payload = UserCreate(
        username="commenter1",
        email="commenter1@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def post(post_repo, author):
    return await post_repo.create_post(PostCreate(
        title="Test post",
        content="Test content",
        author_id=author.id,
    ))


@pytest.mark.asyncio
async def test_create_comment(comment_repo, commenter, post, session):
    payload = CommentCreate(
        content="Ajoyib post!",
        user_id=commenter.id,
        post_id=post.id,
    )

    created = await comment_repo.create_comment(payload)

    assert created.id is not None
    assert created.content == "Ajoyib post!"

    result = await session.execute(select(Comment).where(Comment.id == created.id))
    db_comment = result.scalar_one()

    assert db_comment.content == "Ajoyib post!"
    assert db_comment.user_id == commenter.id
    assert db_comment.post_id == post.id
    assert db_comment.is_deleted is False


@pytest.mark.asyncio
async def test_get_one_comment(comment_repo, commenter, post):
    created = await comment_repo.create_comment(CommentCreate(
        content="Salom", user_id=commenter.id, post_id=post.id,
    ))

    fetched = await comment_repo.get_one_comment(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.content == "Salom"
    assert fetched.post.id == post.id


@pytest.mark.asyncio
async def test_get_one_comment_not_found(comment_repo):
    fetched = await comment_repo.get_one_comment(9999)

    assert fetched is None


@pytest.mark.asyncio
async def test_get_all_comment(comment_repo, commenter, post):
    await comment_repo.create_comment(CommentCreate(
        content="Birinchi", user_id=commenter.id, post_id=post.id,
    ))
    await comment_repo.create_comment(CommentCreate(
        content="Ikkinchi", user_id=commenter.id, post_id=post.id,
    ))

    comments = await comment_repo.get_all_comment()

    assert len(comments) == 2
    contents = {c.content for c in comments}
    assert contents == {"Birinchi", "Ikkinchi"}


@pytest.mark.asyncio
async def test_update_comment(comment_repo, commenter, post):
    created = await comment_repo.create_comment(CommentCreate(
        content="Eski matn", user_id=commenter.id, post_id=post.id,
    ))

    updated = await comment_repo.update_comment(
        created.id,
        CommentUpdate(content="Yangi matn"),
    )

    assert updated.content == "Yangi matn"


@pytest.mark.asyncio
async def test_update_comment_not_found(comment_repo):
    with pytest.raises(Exception):  # HTTPException 404
        await comment_repo.update_comment(9999, CommentUpdate(content="ghost"))


@pytest.mark.asyncio
async def test_delete_comment(comment_repo, commenter, post, session):
    created = await comment_repo.create_comment(CommentCreate(
        content="O'chiriladi", user_id=commenter.id, post_id=post.id,
    ))

    deleted = await comment_repo.delete_comment(created.id)

    assert deleted is True

    result = await session.execute(select(Comment).where(Comment.id == created.id))
    db_comment = result.scalar_one()

    # soft delete: yozuv bazada qoladi
    assert db_comment.is_deleted is True
    assert db_comment.deleted_at is not None

    # get_one_comment endi topmasligi kerak
    fetched = await comment_repo.get_one_comment(created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_comment_not_found(comment_repo):
    result = await comment_repo.delete_comment(9999)

    assert result is None


@pytest.mark.asyncio
async def test_delete_comment_already_deleted(comment_repo, commenter, post):
    created = await comment_repo.create_comment(CommentCreate(
        content="Ikki marta o'chirish", user_id=commenter.id, post_id=post.id,
    ))

    await comment_repo.delete_comment(created.id)
    second_attempt = await comment_repo.delete_comment(created.id)

    assert second_attempt is None