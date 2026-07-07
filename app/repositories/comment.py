from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentUpdate, CommentCreate

from app.core.base import BaseRepository
from app.utils.pagination import PageParams, pagination

from datetime import datetime, timezone


class CommentRepository(BaseRepository):
    async def get_all_comment(self, page_params: PageParams | None = None):
        """
        Barcha commentlarni olish (pagination bilan yoki paginationsiz)
        """
        query = (
            select(Comment)
            .where(Comment.is_deleted == False)
            .options(joinedload(Comment.post).options(joinedload(Post.author)))
        )

        if page_params:
            return await pagination(self.session, query, page_params)

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_one_comment(self, comment_id: int):
        """
        ID bo'yicha comment olish
        """
        query = (
            select(Comment)
            .where(Comment.id == comment_id, Comment.is_deleted == False)
            .options(joinedload(Comment.post).options(joinedload(Post.author)))
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def create_comment(
        self,
        payload: CommentCreate,
        *,
        flush: bool = False,
        commit: bool = True,
    ) -> Comment:
        """
        Yangi comment yaratish
        """
        comment = Comment(**payload.model_dump())
        self.session.add(comment)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()
            await self.session.refresh(comment)

        return comment

    async def update_comment(
        self,
        comment_id: int,
        payload: CommentUpdate,
        *,
        flush: bool = False,
        commit: bool = True
    ) -> Comment:

        comment = await self.get_one_comment(comment_id)

        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(comment, key, value)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()

        return comment

    async def delete_comment(self, comment_id: int) -> bool | None:
        comment = await self.session.get(Comment, comment_id)

        if not comment or comment.is_deleted:
            return None

        comment.is_deleted = True
        comment.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True