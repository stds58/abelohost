"""
PostgreSQL SQLAlchemy адаптеры для репозиториев Message.
Реализует MessageRepository c использованием SQLAlchemy 2.0 + asyncpg.
"""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message as MessageDomain
from backend.app.domain.exceptions.message import MessageError
from backend.app.domain.value_objects.message import MessageId
from backend.app.infra.db.models import Message as ORMMessage


class SQLAlchemyMessageRepository(MessageRepository):
    """
    Реализация MessageRepository c использованием SQLAlchemy + PostgreSQL.
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, message_id: MessageId) -> MessageDomain | None:
        stmt = select(ORMMessage).where(ORMMessage.id == message_id.value)
        result = await self._session.execute(stmt)
        orm_message = result.scalar_one_or_none()

        if orm_message is None:
            return None

        return orm_message.to_domain()

    async def save(self, message: MessageDomain) -> None:
        """
        Сохраняет сообщение
        :param message:
        :return:
        """
        orm_message = ORMMessage(
            id=message.id.value, created_at=message.created_at, text=message.text.value
        )
        self._session.add(orm_message)
        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise MessageError(
                f"Message with id {message.id.value} already exists"
            ) from e


def create_sqlalchemy_message_repository(
    session: AsyncSession,
) -> SQLAlchemyMessageRepository:
    return SQLAlchemyMessageRepository(session=session)
