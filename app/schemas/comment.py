from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentCreateIn(BaseModel):
    content: str
    post_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None


class CommentCreate(CommentUpdate):
    # content: str
    user_id: int
    post_id: int


class CommentResponse(CommentCreate):
    id: int
    created_at: datetime
    updated_at: datetime