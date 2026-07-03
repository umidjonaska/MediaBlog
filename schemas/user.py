from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = Field(UserRole.USER)
    password_hash: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    password_hash: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)