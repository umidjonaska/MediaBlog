from pydantic import BaseModel
from datetime import datetime

class PostUpdate(BaseModel):

    title: str
    content: str


class PostCreate(PostUpdate):

    author_id: int
    content: str



class PostResponse(PostCreate):

    id: int
    likes: int
    created_at: datetime
    updated_at: datetime