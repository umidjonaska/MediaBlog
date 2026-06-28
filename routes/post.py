from fastapi import APIRouter, Depends

from utils.pagination import Page, PageParams, get_page_params
from deps import post_service_dp

from services.post import PostService
from schemas.post import PostResponse, PostCreate, PostUpdate

router = APIRouter()

@router.get("/post", response_model=Page[PostResponse], summary="Barcha postlar")
async def get_all_post(
    page_params: PageParams = Depends(get_page_params),
    _service: PostService = Depends(post_service_dp) 
):
    return await _service.get_all_post(page_params)

@router.get("/post/{post_id}", summary="Id bo'yicha postni olish")
async def get_one_post(
    post_id: int,
    _service: PostService = Depends(post_service_dp)
):
    return await _service.get_one_post(post_id)

@router.post("/post", summary="Yangi Post yaratish")
async def create_post(
    payload: PostCreate,
    _service: PostService = Depends(post_service_dp)
):
    return await _service.create_post(payload)

@router.put("/post", summary="Postni yangilash")
async def update_post(
    post_id: int,
    payload: PostUpdate,
    _service: PostService = Depends(post_service_dp)
):
    return await _service.update_post(post_id, payload)

@router.delete("/post/{post_id}", summary="Postni o'chirish")
async def delete_post(
    post_id: int,
    _service: PostService = Depends(post_service_dp)
):
    return await _service.delete_post(post_id)