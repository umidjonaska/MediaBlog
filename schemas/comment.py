from pydantic import BaseModel
from datetime import datetime

# uuid qilish kerak faqat shu commentnikini
# User_id ni current_user qilish kerak update uchun

class CommentUpdate(BaseModel):
    
    content: str

class CommentCreate(CommentUpdate):

    user_id: int # current_user
    post_id: int

class CommentResponse(CommentCreate):
    
    id: int
    created_at: datetime
    updated_at: datetime