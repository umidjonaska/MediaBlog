from fastapi import APIRouter, Depends, HTTPException, status

from app.utils.pagination import Page, PageParams, get_page_params
from app.deps import order_service_dp
from app.auth.services import get_current_admin_user, get_current_superadmin_user

from app.services.order import OrderService
from app.schemas.order import OrderResponse, OrderCreate, OrderUpdate

router = APIRouter()


@router.get("/order", response_model=Page[OrderResponse], summary="Barcha orderlar (admin/superadmin)")
async def get_all_order(
    page_params: PageParams = Depends(get_page_params),
    _service: OrderService = Depends(order_service_dp),
    current_admin: dict = Depends(get_current_admin_user),
):
    return await _service.get_all_order(page_params)


@router.get("/order/{order_id}", response_model=OrderResponse, summary="Id bo'yicha orderni olish (admin/superadmin)")
async def get_one_order(
    order_id: int,
    _service: OrderService = Depends(order_service_dp),
    current_admin: dict = Depends(get_current_admin_user),
):
    order = await _service.get_one_order(order_id)

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order


@router.post("/order", response_model=OrderResponse, status_code=201, summary="Yangi order yaratish (bot uchun)")
async def create_order(
    payload: OrderCreate,
    _service: OrderService = Depends(order_service_dp),
):
    return await _service.create_order(payload)


@router.put("/order/{order_id}", response_model=OrderResponse, summary="Orderni yangilash (admin/superadmin)")
async def update_order(
    order_id: int,
    payload: OrderUpdate,
    _service: OrderService = Depends(order_service_dp),
    current_admin: dict = Depends(get_current_admin_user),
):
    return await _service.update_order(order_id, payload, current_admin["role"])


@router.delete("/order/{order_id}", summary="Orderni o'chirish (faqat superadmin)")
async def delete_order(
    order_id: int,
    _service: OrderService = Depends(order_service_dp),
    current_superadmin: dict = Depends(get_current_superadmin_user),
):
    return await _service.delete_order(order_id)