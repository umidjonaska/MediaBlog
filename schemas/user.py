from pydantic import BaseModel, EmailStr, constr, Field
from datetime import datetime
from enum import Enum
from typing import Optional

class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'

class UserCreate(BaseModel):

    username: str
    email: EmailStr
    role: UserRole = Field(UserRole.ADMIN)
    password_hash: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None
    

class UserResponse(UserCreate):
    id: int
    updated_at: datetime
    created_at: datetime