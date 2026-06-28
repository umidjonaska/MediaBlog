from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict


class MediaType(str, Enum):
    image = "image"
    video = "video"
    audio = "audio"


class MediaStatus(str, Enum):
    uploading = "uploading"
    processing = "processing"
    uploaded = "uploaded"
    failed = "failed"
    deleted = "deleted"


class MediaBase(BaseModel):
    filename: str
    path: str
    mime_type: str
    type: MediaType
    size: int
    owner_id: int


class MediaCreate(MediaBase):
    thumbnail: str | None = None


class MediaUpdate(BaseModel):
    filename: str | None = None
    path: str | None = None
    mime_type: str | None = None
    type: MediaType | None = None
    size: int | None = None
    owner_id: int | None = None
    thumbnail: str | None = None

    duration: int | None = None
    resolution: str | None = None
    bitrate: int | None = None
    status: MediaStatus | None = None


class MediaResponse(MediaBase):
    id: int

    duration: int | None = None
    resolution: str | None = None
    bitrate: int | None = None
    thumbnail: str | None = None

    status: MediaStatus

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)