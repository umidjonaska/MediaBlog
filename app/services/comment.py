from fastapi import HTTPException, status

from app.core.base import BaseService
from app.utils.pagination import PageParams

from app.repositories.comment import CommentRepository
from app.schemas.comment import CommentCreate, CommentCreateIn, CommentUpdate


class CommentService(BaseService[CommentRepository]):
    async def get_all_comment(self, page_params: PageParams | None = None):
        return await self.repository.get_all_comment(page_params)

    async def get_one_comment(self, comment_id: int):
        return await self.repository.get_one_comment(comment_id)

    async def create_comment(self, payload: CommentCreateIn, current_user_id: int):
        full_payload = CommentCreate(
            content=payload.content,
            post_id=payload.post_id,
            user_id=current_user_id,
        )
        return await self.repository.create_comment(full_payload)

    async def update_comment(self, comment_id: int, payload: CommentUpdate, current_user_id: int):
        comment = await self.repository.get_one_comment(comment_id)

        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        if comment.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")

        return await self.repository.update_comment(comment_id, payload)

    async def delete_comment(self, comment_id: int, current_user_id: int):
        comment = await self.repository.get_one_comment(comment_id)

        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

        if comment.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")

        return await self.repository.delete_comment(comment_id)