"""
Зависимости (Dependencies) для внедрения репозиториев в эндпоинты
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.repositories.message import MessageRepository
from backend.app.db.deps import connection_sqlalchemy_dependency
from backend.app.infra.adapters.sql_alchemy_message_repository import (
    create_sqlalchemy_message_repository,
)


def get_sqlalchemy_repository_write(
    session: Annotated[
        AsyncSession, Depends(connection_sqlalchemy_dependency(commit=True))
    ],
) -> MessageRepository:
    """Получает репозиторий SQLAlchemy для операций записи.

    Args:
        session: Асинхронная сессия SQLAlchemy c авто-коммитом.

    Returns:
        MessageRepository: Экземпляр репозитория.
    """
    return create_sqlalchemy_message_repository(session)


def get_sqlalchemy_repository_read(
    session: AsyncSession = Depends(connection_sqlalchemy_dependency(commit=False)),
) -> MessageRepository:
    """Получает репозиторий SQLAlchemy для операций чтения.

    Args:
        session: Асинхронная сессия SQLAlchemy без авто-коммита.

    Returns:
        MessageRepository: Экземпляр репозитория.
    """
    return create_sqlalchemy_message_repository(session)
