from pathlib import Path

import ffmpeg
from PIL import Image
from sqlalchemy import update

from database.database import AsyncSessionLocal
from models.media import Media
from schemas.media import MediaStatus


async def process_media(
    media_id: int,
    path: str,
    media_type: str,
):
    """
    Background task.

    Image:
        - Thumbnail yaratadi.

    Video:
        - Duration
        - Resolution
        - Bitrate

    Audio:
        - Duration
        - Bitrate
    """

    async with AsyncSessionLocal() as session:

        try:
            # Processing boshlandi
            await session.execute(
                update(Media)
                .where(Media.id == media_id)
                .values(status=MediaStatus.processing)
            )
            await session.commit()

            media_values = {}

            if media_type == "image":
                media_values.update(
                    await process_image(path)
                )

            elif media_type == "video":
                media_values.update(
                    await process_video(path)
                )

            elif media_type == "audio":
                media_values.update(
                    await process_audio(path)
                )

            media_values["status"] = MediaStatus.uploaded

            await session.execute(
                update(Media)
                .where(Media.id == media_id)
                .values(**media_values)
            )

            await session.commit()

        except Exception as e:

            print(f"Media processing error: {e}")

            await session.execute(
                update(Media)
                .where(Media.id == media_id)
                .values(status=MediaStatus.failed)
            )

            await session.commit()


async def process_image(path: str) -> dict:

    img_path = Path(path)
    thumb_path = img_path.parent / f"thumb_{img_path.name}"

    with Image.open(img_path) as img:
        img.thumbnail((300, 300))
        img.save(thumb_path)

    return {
        "thumbnail": str(thumb_path)
    }


async def process_video(path: str) -> dict:

    probe = ffmpeg.probe(path)

    result = {}

    format_info = probe.get("format", {})

    duration = format_info.get("duration")
    bitrate = format_info.get("bit_rate")

    if duration:
        result["duration"] = int(float(duration))

    if bitrate:
        result["bitrate"] = int(bitrate)

    video_stream = next(
        (
            stream
            for stream in probe.get("streams", [])
            if stream.get("codec_type") == "video"
        ),
        None,
    )

    if video_stream:
        width = video_stream.get("width")
        height = video_stream.get("height")

        if width and height:
            result["resolution"] = f"{width}x{height}"

    return result


async def process_audio(path: str) -> dict:

    probe = ffmpeg.probe(path)

    result = {}

    format_info = probe.get("format", {})

    duration = format_info.get("duration")
    bitrate = format_info.get("bit_rate")

    if duration:
        result["duration"] = int(float(duration))

    if bitrate:
        result["bitrate"] = int(bitrate)

    return result