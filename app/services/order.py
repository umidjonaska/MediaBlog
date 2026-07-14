from fastapi import HTTPException, status

from app.core.base import BaseService
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.schemas.user import UserRole
from app.utils.pagination import PageParams


class OrderService(BaseService[OrderRepository]):
    async def get_all_order(self, page_params: PageParams | None = None):
        return await self.repository.get_all_order(page_params)

    async def get_one_order(self, order_id: int):
        return await self.repository.get_one_order(order_id)

    async def create_order(self, payload: OrderCreate):
        return await self.repository.create_order(payload)

    async def update_order(self, order_id: int, payload: OrderUpdate, current_user_role: str):
        role = UserRole(current_user_role)

        if role == UserRole.ADMIN:
            changed_fields = payload.model_dump(exclude_unset=True).keys()
            if changed_fields - {"status"}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin faqat buyurtma statusini o'zgartira oladi",
                )

        return await self.repository.update_order(order_id, payload)

    async def delete_order(self, order_id: int):
        return await self.repository.delete_order(order_id)