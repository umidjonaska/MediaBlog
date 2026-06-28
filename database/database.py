from core.config import config
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = (
    f"{config.database.db_connection}://"
    f"{config.database.db_username}:{config.database.db_password}@"
    f"{config.database.db_host}:{config.database.db_port}/"
    f"{config.database.db_database}"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True,
                             pool_size=20, max_overflow=20,
                             pool_pre_ping=True, # Ulanish uzilib qolsa qayta tiklaydi. Harbir so'rovdan oldin ping yuboradi agar server bilan aloqa bo'lmasa uni ulaydi.
                             )

# SessionLocal yaratish
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception as e:
            await db.rollback()  # Xato yuzaga kelsa, tranzaksiyani orqaga qaytarish
            raise e  # Xatoni qaytarish
        finally:
            await db.close()  # Sessiyani yopish