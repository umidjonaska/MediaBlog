from fastapi import UploadFile, BackgroundTasks, HTTPException

from core.base import BaseService
from core import exception
from utils.pagination import PageParams
from schemas.media import MediaCreate, MediaStatus, MediaUpdate
from repositories.media import MediaRepository

from utils.file import save_file, detect_media_type
from utils.media import process_media


class MediaService(BaseService[MediaRepository]):

    async def get_all_media(self, page_params: PageParams):
        return await self.repository.get_all_media(page_params)

    async def get_one_media(self, media_id: int):
        return await self.repository.get_one_media(media_id)

    async def create_media(self, payload: MediaCreate):
        media_id = await self.repository.create_media(payload)
        return {"id": media_id, "status": MediaStatus.uploading}


    async def update_media(
        self,
        media_id: int,
        payload: MediaUpdate,
    ):
        media = await self.repository.get_one_media(media_id)

        if not media:
            return exception.NotFoundResponse()

        updated = await self.repository.update_media(
            media_id,
            payload,
        )

        return updated

    async def delete_media(self, media_id: int):
        media = await self.repository.get_one_media(media_id)
        if not media:
            return exception.NotFoundResponse()

        return await self.repository.delete_media(media_id)

    async def upload(
        self,
        file: UploadFile,
        owner_id: int,
        bg: BackgroundTasks,
    ):
        content_type = file.content_type

        if content_type is None:
            raise HTTPException(
                status_code=400,
                detail="Content-Type is required."
            )
        
        media_type = detect_media_type(file.content_type or "")

        try:
            filename, path, size = await save_file(file, media_type)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"File upload failed: {e}"
            )

        payload = MediaCreate(
            filename=filename,
            path=path,
            mime_type=content_type,
            type=media_type,
            size=size,
            owner_id=owner_id,
        )

        media_id = await self.repository.create_media(payload)
        if media_id is None:
            raise HTTPException(
                status_code=500,
                detail="Media record was not created"
            )

        bg.add_task(
            process_media,
            media_id,
            path,
            media_type,
        )

        return {
            "id": media_id,
            "status": MediaStatus.uploading,
        }