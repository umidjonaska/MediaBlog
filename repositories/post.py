from fastapi import HTTPException
from datetime import datetime, timezone

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import selectinload, joinedload

from models.post import Post
from schemas.post import PostCreate, PostUpdate

from core.base import BaseRepository
from utils.pagination import PageParams, pagination


class PostRepository(BaseRepository):
    async def get_all_post(self, page_params: PageParams | None = None):
        query = (
            select(Post)
            .where(Post.is_deleted == False)
            .options(joinedload(Post.author), selectinload(Post.comments))
        )
        if page_params:
            return await pagination(self.session, query, page_params)
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_one_post(self, post_id: int):
        query = (
            select(Post)
            .where(Post.id == post_id, Post.is_deleted == False)
            .options(selectinload(Post.author), joinedload(Post.comments))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def create_post(
        self,
        payload: PostCreate,
        *,
        flush: bool = False,
        commit: bool = True,
    ) -> Post:
        post = Post(**payload.model_dump())
        self.session.add(post)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()
            await self.session.refresh(post)

        return post

    async def update_post(
        self,
        post_id: int,
        payload: PostUpdate,
        *,
        flush: bool = False,
        commit: bool = True
    ) -> Post:

        post = await self.get_one_post(post_id)

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(post, key, value)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()

        return post

    async def delete_post(self, post_id: int) -> bool | None:
        post = await self.session.get(Post, post_id)
        if not post or post.is_deleted:
            return None

        post.is_deleted = True
        post.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True
