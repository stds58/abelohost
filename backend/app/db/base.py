"""
Рекомендуемые соглашения для именования constraints
Это особенно важно для Alembic (миграции)

"ix": "ix_%(column_0_label)s",  # индексы
"uq": "uq_%(table_name)s_%(column_0_name)s",  # уникальные constraints
"ck": "ck_%(table_name)s_%(constraint_name)s",  # check constraints
"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign keys
"pk": "pk_%(table_name)s",  # первичные ключи
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped

from backend.app.db.annotations import CreatedAt, UUIDPk

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

    id: Mapped[UUIDPk]
    created_at: Mapped[CreatedAt]
