from abc import ABC
from typing import TypeVar, Generic

from sqlalchemy.ext.asyncio import AsyncSession

class BaseRepository(ABC):
    """
    Ma'lumotlar bazasi bilan ishlash uchun bazaviy sinf.

    Attributes:
        session (AsyncSession): Filial bazasi uchun sessiya.
        db_main_session (AsyncSession | None): Asosiy baza uchun sessiya (ixtiyoriy).
    """

    def __init__(self, session: AsyncSession, db_main_session: AsyncSession = None):
        self.session = session
        self.db_main_session = db_main_session


T = TypeVar("T")

class BaseService(Generic[T]):
    """
    Bazaviy servis sinfi, ma'lumotlar bazasi bilan ishlash uchun repository qatlamini boshqaradi.

    Attributes:
        repository (T): Repository obyekti, ma'lumotlar bazasi operatsiyalari uchun ishlatiladi.
    """
    def __init__(self, repository: T):
        """
        BaseService ni boshlash.

        Args:
            repository (T): Repository obyekti.
        """
        self.repository = repository

    def get_repository(self):
        """
        Repository obyekti qaytaradi.

        Returns:
            T: Repository obyekti.
        """
        return self.repository