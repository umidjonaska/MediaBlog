from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.user import User
from .schema import TokenResponse, Refresh
from .services import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_token,
    user_refresh_token_update,
)
from database.database import get_db
from auth.services import get_current_user

auth_route = APIRouter(tags=["Auth"])


@auth_route.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol xato",
        )

    access_token = await create_access_token({"sub": user.email})
    refresh_token = await create_refresh_token({"sub": user.email})

    await user_refresh_token_update(db, user.email, refresh_token)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
        },
        "role": user.role,
        "token_type": "bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@auth_route.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh: Refresh,
    db: AsyncSession = Depends(get_db),
):
    payload = await verify_token(refresh.token)
    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Token yaroqsiz")

    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user or user.refresh_token != refresh.token:
        raise HTTPException(status_code=401, detail="Token yaroqsiz")

    access_token = await create_access_token({"sub": email})
    refresh_token = await create_refresh_token({"sub": email})

    await user_refresh_token_update(db, email, refresh_token)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "rasm": user.rasm,
        },
        "role": user.role,
        "token_type": "bearer",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@auth_route.get("/me")
async def read_current_user(current_user=Depends(get_current_user)):
    return current_user
