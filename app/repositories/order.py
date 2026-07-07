from fastapi import HTTPException
from sqlalchemy import select

from datetime import datetime, timezone

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate

from app.core.base import BaseRepository
from app.utils.pagination import PageParams, pagination


class OrderRepository(BaseRepository):
    async def get_all_order(self, page_params: PageParams | None = None):
        query = select(Order).where(Order.is_deleted == False)

        if page_params:
            return await pagination(self.session, query, page_params)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_order(self, order_id: int):
        query = select(Order).where(Order.id == order_id, Order.is_deleted == False)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_order(
        self,
        payload: OrderCreate,
        *,
        flush: bool = False,
        commit: bool = True,
    ) -> Order:
        order = Order(**payload.model_dump())
        self.session.add(order)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()
            await self.session.refresh(order)

        return order

    async def update_order(
        self,
        order_id: int,
        payload: OrderUpdate,
        *,
        flush: bool = False,
        commit: bool = True,
    ) -> Order:
        order = await self.get_one_order(order_id)

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, key, value)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()

        return order

    async def delete_order(self, order_id: int) -> bool | None:
        order = await self.session.get(Order, order_id)
        if not order or order.is_deleted:
            return None

        order.is_deleted = True
        order.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True