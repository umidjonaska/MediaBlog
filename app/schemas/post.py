from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostCreateIn(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int


class PostResponse(PostCreate):
    id: int
    likes: int
    created_at: datetime
    updated_at: datetime