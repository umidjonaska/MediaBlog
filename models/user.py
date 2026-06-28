from sqlalchemy import Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from schemas.user import UserRole
from database.database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash : Mapped[str]= mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.utcnow)
    
    
    # Relationships
    posts: Mapped[str] = relationship("Post", back_populates="author")
    comments: Mapped[str] = relationship("Comment", back_populates="user")
    media_list = relationship("Media", back_populates="owner")