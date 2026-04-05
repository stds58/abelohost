from typing import Annotated

import asyncpg
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.repositories.message import MessageRepository
from backend.app.db.deps import (
    connection_asyncpg_dependency,
    connection_sqlalchemy_dependency,
)
from backend.app.infra.adapters.asyncpg_message_repository import (
    create_asyncpg_message_repository,
)
from backend.app.infra.adapters.in_memory_message_repository import (
    in_memory_message_repository_instance,
)
from backend.app.infra.adapters.sql_alchemy_message_repository import (
    create_sqlalchemy_message_repository,
)


def get_sqlalchemy_repository_write(
    # session: AsyncSession = Depends(connection_sqlalchemy_dependency(commit=True))
    session: Annotated[
        AsyncSession, Depends(connection_sqlalchemy_dependency(commit=True))
    ],
) -> MessageRepository:
    return create_sqlalchemy_message_repository(session)


def get_sqlalchemy_repository_read(
    session: AsyncSession = Depends(connection_sqlalchemy_dependency(commit=False)),
) -> MessageRepository:
    return create_sqlalchemy_message_repository(session)


def get_asyncpg_repository(
    conn: asyncpg.Connection = Depends(connection_asyncpg_dependency()),
) -> MessageRepository:
    return create_asyncpg_message_repository(conn)


def get_in_memory_repository() -> MessageRepository:
    return in_memory_message_repository_instance
