"""
Зависимости (Dependencies) для внедрения репозиториев в эндпоинты
"""

import asyncpg
from fastapi import Depends

from backend.app.application.repositories.message import MessageRepository
from backend.app.db.deps import connection_asyncpg_dependency
from backend.app.infra.adapters.asyncpg_message_repository import (
    create_asyncpg_message_repository,
)


def get_asyncpg_repository(
    conn: asyncpg.Connection = Depends(connection_asyncpg_dependency()),
) -> MessageRepository:
    """Получает репозиторий на базе asyncpg.

    Args:
        conn: Активное соединение asyncpg внутри транзакции.

    Returns:
        MessageRepository: Экземпляр репозитория.
    """
    return create_asyncpg_message_repository(conn)
