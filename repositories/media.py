from fastapi import HTTPException
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.media import Media
from schemas.media import MediaCreate, MediaStatus, MediaUpdate, MediaResponse

from core.base import BaseRepository
from utils.pagination import PageParams, pagination, Page


class MediaRepository(BaseRepository):
    # Barcha medialarni olish (pagination bilan yoki paginationsiz)
    async def get_all_media(
        self,
        page_params: PageParams,
    ):
        query = (
            select(Media)
            .where(Media.status != MediaStatus.deleted)
            .options(selectinload(Media.owner))
        )

        return await pagination(
            self.session,
            query,
            page_params,
        )

    # ID bo‘yicha bitta media olish
    async def get_one_media(self, media_id: int):
        query = (
            select(Media)
            .where(Media.id == media_id)
            .options(selectinload(Media.owner))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # Yangi media yaratish
    async def create_media(
        self,
        payload: MediaCreate,
    ) -> int:
        media = Media(
            **payload.model_dump(),
            status=MediaStatus.uploading
        )

        self.session.add(media)
        await self.session.commit()
        await self.session.refresh(media)

        return media.id

    # Media ma'lumotlarini yangilash
    async def update_media(
        self,
        media_id: int,
        payload: MediaUpdate,
        *,
        flush: bool = False,
        commit: bool = True
    ) -> Media:

        media = await self.get_one_media(media_id)

        if not media:
            raise HTTPException(status_code=404, detail="Media not found")

        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(media, key, value)

        if flush:
            await self.session.flush()

        if commit:
            await self.session.commit()

        return media

    # Media soft delete
    async def delete_media(self, media_id: int) -> bool | None:
        media = await self.session.get(Media, media_id)
        if not media:
            return None

        media.status = MediaStatus.deleted
        media.deleted_at = datetime.now(timezone.utc)
        await self.session.commit()
        return True