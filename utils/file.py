import uuid
from pathlib import Path

from fastapi import UploadFile

from schemas.media import MediaType


MEDIA_ROOT = Path("media")


async def save_file(
    file: UploadFile,
    folder: str,
) -> tuple[str, str, int]:
    """
    Upload qilingan faylni diskka saqlaydi.

    Returns:
        filename
        full_path
        size(bytes)
    """

    suffix = Path(file.filename or "").suffix
    filename = f"{uuid.uuid4()}{suffix}"

    folder_path = MEDIA_ROOT / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    full_path = folder_path / filename

    size = 0

    with open(full_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):  # 1 MB
            size += len(chunk)
            buffer.write(chunk)

    await file.close()

    return filename, str(full_path), size


def detect_media_type(mime: str) -> MediaType:
    """
    MIME type bo'yicha media turini aniqlaydi.
    """

    mime = mime.lower()

    if mime.startswith("image/"):
        return MediaType.image

    if mime.startswith("video/"):
        return MediaType.video

    if mime.startswith("audio/"):
        return MediaType.audio

    raise ValueError(f"Unsupported media type: {mime}")