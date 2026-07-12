import asyncio

from app.database.database import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserRole
from app.auth.services import get_password_hash

# Barcha modellarni import qilish - relationship() satrlarini to'g'ri
# hal qilish uchun ular SQLAlchemy registry'da ro'yxatdan o'tgan bo'lishi kerak
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.media import Media
from app.models.order import Order


async def main():
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        payload = UserCreate(
            username="superadmin",
            email="superadmin@mail.ru",
            role=UserRole.SUPERADMIN,
            password_hash=get_password_hash("xavfsiz_parol_shu_yerga"),
        )
        user = await repo.create_user(payload)
        print(f"Superadmin yaratildi: id={user.id}")


if __name__ == "__main__":
    asyncio.run(main())