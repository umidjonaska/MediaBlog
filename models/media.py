# models/media.py
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
    DateTime,
    BigInteger,
    Enum,
)
from database.database import Base
from schemas.media import MediaStatus, MediaType


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    type: Mapped[MediaType] = mapped_column(
        Enum(MediaType, name="media_type_enum"),
        nullable=False
    )

    size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    thumbnail: Mapped[str | None] = mapped_column(String(500))
    duration: Mapped[int | None] = mapped_column(Integer)
    resolution: Mapped[str | None] = mapped_column(String(50))
    bitrate: Mapped[int | None] = mapped_column(Integer)

    status: Mapped[MediaStatus] = mapped_column(
        Enum(MediaStatus, name="media_status_enum"),
        default=MediaStatus.uploading,
        nullable=False
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # relations
    owner = relationship("User", back_populates="media_list")
