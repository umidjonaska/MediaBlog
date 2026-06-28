from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


class Refresh(BaseModel):
    token: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email: str
    username: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    role: str
    rasm: Optional[str] = None


class TokenResponse(BaseModel):
    user: UserResponse
    role: str
    token_type: str
    access_token: str
    refresh_token: str


class ImmResponse(BaseModel):
    email: str
