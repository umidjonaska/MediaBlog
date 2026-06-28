from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta

import orjson

from core.config import config
from database.database import get_db
from models.user import User
from schemas.user import UserRole
from core.redis_cli import RedisCLI


# SECURITY
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



# PASSWORD
async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



# JWT
async def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            config.app.secret_key,
            algorithms=[config.app.algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=config.app.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        config.app.secret_key,
        algorithm=config.app.algorithm
    )


async def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=config.app.refresh_token_expire_days
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        config.app.secret_key,
        algorithm=config.app.algorithm
    )



# USER HELPERS
def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }


async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user



# CURRENT USER
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    payload = await verify_token(token)
    email = payload.get("sub")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    redis_cli = RedisCLI()

    cached = redis_cli.get(email)

    # 🔹 CACHE HIT
    if cached:
        if isinstance(cached, (bytes, bytearray)):
            cached = cached.decode("utf-8")

        return orjson.loads(cached)

    # 🔹 CACHE MISS → DB GA BORISH
    user = await get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user_data = serialize_user(user)

    redis_cli.set(
        email,
        orjson.dumps(user_data),
        ex=3600
    )

    return user_data


# ADMIN CHECK
async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
):
    if UserRole(current_user["role"]) != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Ruxsat yo‘q"
        )
    return current_user



# REFRESH TOKEN UPDATE
async def user_refresh_token_update(
    db: AsyncSession,
    email: str,
    token: str
) -> bool:
    if not token:
        raise HTTPException(
            status_code=422,
            detail="Token bo‘sh"
        )

    stmt = (
        update(User)
        .where(User.email == email)
        .values(refresh_token=token)
    )
    await db.execute(stmt)
    await db.commit()

    return True
