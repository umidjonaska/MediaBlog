from fastapi import HTTPException, status

from app.core.base import BaseService
from app.repositories.post import PostRepository
from app.schemas.post import PostCreate, PostUpdate
from app.utils.pagination import PageParams


class PostService(BaseService[PostRepository]):
    async def get_all_post(self, page_params: PageParams | None = None):
        return await self.repository.get_all_post(page_params)

    async def get_one_post(self, post_id: int):
        return await self.repository.get_one_post(post_id)

    async def create_post(self, payload: PostCreate):
        return await self.repository.create_post(payload)

    async def update_post(self, post_id: int, payload: PostUpdate, current_user_id: int):
        post = await self.repository.get_one_post(post_id)

        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if post.author_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")

        return await self.repository.update_post(post_id, payload)

    async def delete_post(self, post_id: int, current_user_id: int):
        post = await self.repository.get_one_post(post_id)

        if post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

        if post.author_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ruxsat yo'q")

        return await self.repository.delete_post(post_id)