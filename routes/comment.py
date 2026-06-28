from fastapi import APIRouter, Depends

from utils.pagination import Page, PageParams, get_page_params
from deps import comment_service_dp

from services.comment import CommentService
from schemas.comment import CommentResponse, CommentCreate, CommentUpdate

router = APIRouter()

@router.get("/comment", response_model=Page[CommentResponse], summary="Barcha commentlar")
async def get_all_comment(
    page_params: PageParams = Depends(get_page_params),
    _service: CommentService = Depends(comment_service_dp) 
):
    return await _service.get_all_comment(page_params)

@router.get("/comment/{comment_id}", summary="Id bo'yicha commentni olish")
async def get_one_comment(
    comment_id: int,
    _service: CommentService = Depends(comment_service_dp)
):
    return await _service.get_one_comment(comment_id)

@router.post("/comment", summary="Yangi comment yaratish")
async def create_comment(
    payload: CommentCreate,
    _service: CommentService = Depends(comment_service_dp)
):
    return await _service.create_comment(payload)

@router.put("/comment", summary="commentni yangilash")
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    _service: CommentService = Depends(comment_service_dp)
):
    return await _service.update_comment(comment_id, payload)

@router.delete("/comment/{comment_id}", summary="commentni o'chirish")
async def delete_comment(
    comment_id: int,
    _service: CommentService = Depends(comment_service_dp)
):
    return await _service.delete_comment(comment_id)