from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException

from services.media import MediaService
from models.user import User
from schemas.media import MediaCreate, MediaStatus, MediaResponse, MediaUpdate
from deps import media_service_dp
from utils.pagination import Page, PageParams, get_page_params
from utils.file import save_file, detect_media_type
from utils.media import process_media
from auth.services import get_current_user


router = APIRouter()

@router.get("/media", summary="Barcha medialarni olish")
async def router_get_all_media(
    #current_user: User = Depends(get_current_user),
    page_params: PageParams = Depends(get_page_params),
    _service: MediaService = Depends(media_service_dp)
) -> Page[MediaResponse]:
    return await _service.get_all_media(page_params)

@router.get("/media_one",summary="Media haqida to'liq ma'lumot olish")
async def router_get_one( 
    id: int,
    #current_user: User = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp)
):
    return await _service.get_one(id)


@router.post("/media/upload", summary="Media faylni yuklash va background task orqali processing qilish")
async def upload_media(
    file: UploadFile,
    bg: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp)
):
    result = await _service.upload(file, current_user["id"], bg)
    return result

@router.put("/media_update",summary="Media haqidagi ma'lumotni yangilash")
async def router_update(
    id: int,
    payload: MediaUpdate,
    #current_user: User = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp)
):
    return await _service.update(id, payload)

@router.delete("/media_delete",summary="Chiqim o'chirish")
async def router_delete(
    id: int,
    #current_user: User = Depends(get_current_user),
    _service: MediaService = Depends(media_service_dp)
):
    return await _service.delete(id)