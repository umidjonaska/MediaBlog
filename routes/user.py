from fastapi import APIRouter, Depends

from utils.pagination import Page, PageParams, get_page_params
from deps import user_service_dp

from services.user import UserService
from schemas.user import UserResponse, UserCreate, UserUpdate

router = APIRouter()

@router.get("/users/", response_model=Page[UserResponse], summary="Barcha userlar ma'lumoti")
async def router_get_all(
    page_params: PageParams = Depends(get_page_params),
    _service: UserService = Depends(user_service_dp),
):
    return await _service.get_all_user(page_params)


@router.get("/users/{user_id}/", summary="Aniq user ma'lumoti")
async def router_get_one(
    user_id: int,
    _service: UserService = Depends(user_service_dp)
):
    return await _service.get_one_user(user_id)

@router.post("/users/", summary="Yangi user qo'shish", status_code=201)
async def router_create(
    payload: UserCreate,
    _service: UserService = Depends(user_service_dp)
):
    return await _service.create_user(payload)

@router.put("/users/", summary="User malumotlarini yangilash")
async def router_update(
    user_id: int,
    payload: UserUpdate,
    _service: UserService = Depends(user_service_dp)
):
    return await _service.update_user(user_id, payload)