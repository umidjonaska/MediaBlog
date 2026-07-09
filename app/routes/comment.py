from fastapi import APIRouter, Depends, HTTPException, status

from app.utils.pagination import Page, PageParams, get_page_params
from app.deps import comment_service_dp
from app.auth.services import get_current_user

from app.services.comment import CommentService
from app.schemas.comment import CommentResponse, CommentCreateIn, CommentUpdate

router = APIRouter()


@router.get("/comment", response_model=Page[CommentResponse], summary="Barcha commentlar")
async def get_all_comment(
    page_params: PageParams = Depends(get_page_params),
    _service: CommentService = Depends(comment_service_dp),
    # current_user: dict = Depends(get_current_user),
):
    return await _service.get_all_comment(page_params)


@router.get("/comment/{comment_id}", response_model=CommentResponse, summary="Id bo'yicha commentni olish")
async def get_one_comment(
    comment_id: int,
    _service: CommentService = Depends(comment_service_dp),
    current_user: dict = Depends(get_current_user),
):
    comment = await _service.get_one_comment(comment_id)

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    return comment


@router.post("/comment", response_model=CommentResponse, status_code=201, summary="Yangi comment yaratish")
async def create_comment(
    payload: CommentCreateIn,
    _service: CommentService = Depends(comment_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.create_comment(payload, current_user["id"])


@router.put("/comment/{comment_id}", response_model=CommentResponse, summary="commentni yangilash")
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    _service: CommentService = Depends(comment_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.update_comment(comment_id, payload, current_user["id"])


@router.delete("/comment/{comment_id}", summary="commentni o'chirish")
async def delete_comment(
    comment_id: int,
    _service: CommentService = Depends(comment_service_dp),
    current_user: dict = Depends(get_current_user),
):
    return await _service.delete_comment(comment_id, current_user["id"])