from fastapi import APIRouter, Depends, UploadFile, BackgroundTasks, HTTPException, status

from app.services.media import MediaService
from app.schemas.media import MediaResponse, MediaUpdate
from app.deps import media_service_dp
from app.utils.pagination import Page, PageParams, get_page_params
from app.auth.services import get_current_user

router = APIRouter()


@router.get("/media", response_model=Page[MediaResponse], summary="Barcha medialarni olish")
async def router_get_all_media(
    current_user: dict = Depends(get_current_user),
    page_params: PageParams = Depends(get_page_params),
    _service: MediaService = Depends(media_service_dp),
):
    return await _service.get_all_media(page_params)


@router.get("/media/{media_id}", response_model=MediaResponse, summary="Media haqida to'liq ma'lumot olish")
async def router_get_one(
    media_id: int,
    current_user: dict = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp),
):
    media = await _service.get_one_media(media_id)

    if media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    return media


@router.post("/media/upload", summary="Media faylni yuklash va background task orqali processing qilish")
async def upload_media(
    file: UploadFile,
    bg: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp),
):
    return await _service.upload(file, current_user["id"], bg)


@router.put("/media/{media_id}", response_model=MediaResponse, summary="Media haqidagi ma'lumotni yangilash")
async def router_update(
    media_id: int,
    payload: MediaUpdate,
    current_user: dict = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp),
):
    return await _service.update_media(media_id, payload, current_user["id"])


@router.delete("/media/{media_id}", summary="Media o'chirish")
async def router_delete(
    media_id: int,
    current_user: dict = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp),
):
    return await _service.delete_media(media_id, current_user["id"])