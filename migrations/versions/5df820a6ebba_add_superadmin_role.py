"""add superadmin role

Revision ID: 5df820a6ebba
Revises: e2aaf9a6e566
Create Date: 2026-07-12 07:14:26.968918

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5df820a6ebba'
down_revision: Union[str, Sequence[str], None] = 'e2aaf9a6e566'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("COMMIT")  # ALTER TYPE ... ADD VALUE tranzaksiya tashqarisida bo'lishi kerak
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'SUPERADMIN'")


def downgrade() -> None:
    # Postgres enum qiymatini olib tashlashni to'g'ridan-to'g'ri qo'llab-quvvatlamaydi.
    # Kerak bo'lsa, yangi enum yaratish -> ustunni ko'chirish -> eskisini o'chirish orqali qilinadi.
    pass