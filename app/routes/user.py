from fastapi import APIRouter, Depends, HTTPException, status

from app.utils.pagination import Page, PageParams, get_page_params
from app.deps import user_service_dp
from app.auth.services import get_current_user

from app.services.user import UserService
from app.schemas.user import UserResponse, UserCreate, UserUpdate

router = APIRouter()


@router.get("/users/", response_model=Page[UserResponse], summary="Barcha userlar ma'lumoti")
async def router_get_all(
    page_params: PageParams = Depends(get_page_params),
    _service: UserService = Depends(user_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.get_all_user(page_params)


@router.get("/users/{user_id}/", response_model=UserResponse, summary="Aniq user ma'lumoti")
async def router_get_one(
    user_id: int,
    _service: UserService = Depends(user_service_dp),
    current_user: dict = Depends(get_current_user),
):
    user = await _service.get_one_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.post("/users/", summary="Yangi user qo'shish", status_code=201)
async def router_create(
    payload: UserCreate,
    _service: UserService = Depends(user_service_dp),
):
    return await _service.create_user(payload)


@router.put("/users/", response_model=UserResponse, summary="Joriy user ma'lumotlarini yangilash")
async def router_update(
    payload: UserUpdate,
    _service: UserService = Depends(user_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.update_user(current_user["id"], payload)

@router.delete("/users/{user_id}", summary="ID bo'yicha userni o'chirish")
async def router_delete(
    user_id: int,
    _service: UserService = Depends(user_service_dp),
):
    return await _service.delete_user(user_id)