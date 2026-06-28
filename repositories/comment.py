from fastapi import HTTPException

from sqlalchemy import select, delete, insert
from sqlalchemy.orm import joinedload

from models.comment import Comment
from models.post import Post
from schemas.comment import CommentUpdate, CommentCreate

from core.base import BaseRepository
from utils.pagination import PageParams, pagination


class CommentRepository(BaseRepository):
    async def get_all_comment(self, page_params: PageParams | None = None):
        """
        Barcha commentlarni olish (pagination bilan yoki paginationsiz)
        """
        query = select(Comment).options(joinedload(Comment.post).options(joinedload(Post.author)))

        if page_params:
            return await pagination(self.session, query, page_params)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_comment(self, comment_id: int):
        """
        ID bo'yicha comment olish
        """
        query = select(Comment).where(Comment.id == comment_id).options(
            joinedload(Comment.post).options(joinedload(Post.author)
))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_comment(
        self,
        payload: CommentCreate,
        *,
        flush: bool = False,
        commit: bool = True
    ) -> int | None:
        """
        Yangi comment yaratish
        """
        query = insert(Comment).values(payload.model_dump())
        result = await self.session.execute(query)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()

        return None

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

        if not comment:
            return None

        await self.session.delete(comment)
        await self.session.commit()
        return True

    # async def delete_all_comments(self) -> int:
    #     """
    #     Barcha commentlarni o'chirish (EHTIYOT!)
    #     """
    #     query = delete(Comment)
    #     result = await self.session.execute(query)
    #     await self.session.commit()
    #     return result.rowcount
