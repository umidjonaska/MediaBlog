from core.base import BaseService
from core import exception
from utils.pagination import PageParams

from repositories.comment import CommentRepository
from schemas.comment import CommentCreate, CommentUpdate

class CommentService(BaseService[CommentRepository]):
    async def get_all_comment(self, page_params: PageParams | None = None):
        return await self.repository.get_all_comment(page_params)
    
    async def get_one_comment(self, comment_id: int):
        return await self.repository.get_one_comment(comment_id)
    
    async def create_comment(self, payload: CommentCreate):
        await self.repository.create_comment(payload)
        return exception.CreatedResponse()
    
    async def update_comment(self, comment_id: int, payload: CommentUpdate):
        result = await self.repository.get_one_comment(comment_id)
        if not result:
            return exception.NotFoundResponse()
        
        return await self.repository.update_comment(comment_id, payload)
    
    async def delete_comment(self, comment_id: int):
        result = await self.repository.get_one_comment(comment_id)
        if not result:
            return exception.NotFoundResponse()
        
        return await self.repository.delete_comment(comment_id)