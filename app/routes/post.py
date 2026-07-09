from fastapi import APIRouter, Depends, HTTPException, status

from app.utils.pagination import Page, PageParams, get_page_params
from app.deps import post_service_dp
from app.auth.services import get_current_user

from app.services.post import PostService
from app.schemas.post import PostResponse, PostCreate, PostCreateIn, PostUpdate

router = APIRouter()


@router.get("/post", response_model=Page[PostResponse], summary="Barcha postlar")
async def get_all_post(
    page_params: PageParams = Depends(get_page_params),
    _service: PostService = Depends(post_service_dp),
    # current_user: dict = Depends(get_current_user),
):
    return await _service.get_all_post(page_params)


@router.get("/post/{post_id}", response_model=PostResponse, summary="Id bo'yicha postni olish")
async def get_one_post(
    post_id: int,
    _service: PostService = Depends(post_service_dp),
    current_user: dict = Depends(get_current_user),
):
    post = await _service.get_one_post(post_id)

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    return post


@router.post("/post", response_model=PostResponse, status_code=201, summary="Yangi Post yaratish")
async def create_post(
    payload: PostCreateIn,
    _service: PostService = Depends(post_service_dp),
    current_user: dict = Depends(get_current_user),
):
    full_payload = PostCreate(**payload.model_dump(), author_id=current_user["id"])
    return await _service.create_post(full_payload)


@router.put("/post/{post_id}", response_model=PostResponse, summary="Postni yangilash")
async def update_post(
    post_id: int,
    payload: PostUpdate,
    _service: PostService = Depends(post_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.update_post(post_id, payload, current_user["id"])


@router.delete("/post/{post_id}", summary="Postni o'chirish")
async def delete_post(
    post_id: int,
    _service: PostService = Depends(post_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.delete_post(post_id, current_user["id"])