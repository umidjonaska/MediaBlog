from sqlalchemy import Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.database import Base
from datetime import datetime


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id")) # current_user qilish kerak
    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)


    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")