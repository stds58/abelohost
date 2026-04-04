from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.repositories.message import MessageRepository
from backend.app.application.use_cases.create_message import CreateMessageUseCase
from backend.app.application.use_cases.get_message import GetMessageUseCase
from backend.app.db.deps import connection
from backend.app.infra.adapters.sql_alchemy_message_repository import (
    get_sqlalchemy_message_repository,
)


def get_message_repository(
    session: AsyncSession = Depends(connection(commit=True)),
) -> MessageRepository:
    """Фабрика репозитория для DI"""
    return get_sqlalchemy_message_repository(session)


def get_get_message_use_case(
    repository: MessageRepository = Depends(get_message_repository),
) -> GetMessageUseCase:
    """Фабрика Use Case для GET"""
    return GetMessageUseCase(repository=repository)


def get_create_message_use_case(
    repository: MessageRepository = Depends(get_message_repository),
) -> CreateMessageUseCase:
    """Фабрика Use Case для POST"""
    return CreateMessageUseCase(repository=repository)
