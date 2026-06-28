from fastapi import HTTPException, status
from core.base import BaseService
from core import exception
from utils.pagination import PageParams

from auth.services import get_password_hash
from repositories.user import UserRepository
from schemas.user import UserCreate, UserUpdate

class UserService(BaseService[UserRepository]):
    async def get_all_user(self, page_params: PageParams | None = None):
        return await self.repository.get_all_user(page_params)
    
    async def get_one_user(self, user_id: int):
        return await self.repository.get_one_user(user_id)
    
    async def create_user(self, payload: UserCreate):
        payload.password_hash = await get_password_hash(payload.password_hash)

        user = await self.repository.create_user(payload)
        return {"id": user.id}

    async def update_user(self, user_id: int, payload: UserUpdate):
        user = await self.repository.get_one_user(user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return await self.repository.update_user(user_id, payload)
    