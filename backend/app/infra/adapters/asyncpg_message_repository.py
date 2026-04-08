"""
asyncpg адаптер для репозиториев Message.
Реализует MessageRepository c использованием asyncpg.
"""

import asyncpg

from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message as MessageDomain
from backend.app.domain.exceptions.message import MessageError
from backend.app.domain.value_objects.message import MessageId


class AsyncpgMessageRepository(MessageRepository):
    """
    Реализация MessageRepository c использованием asyncpg.
    Принимает уже открытое соединение (Connection) из DI.
    """

    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn

    async def get_by_id(self, message_id: MessageId) -> MessageDomain | None:
        """
        используем get_asyncpg_pool
        :param message_id:
        :return:
        """
        row = await self._conn.fetchrow(
            """
            SELECT id, created_at, text::TEXT AS text
            FROM messages
            WHERE id = $1
            """,
            message_id.value,
        )

        if not row:
            return None

        data = {
            "id": str(row["id"]),
            "created_at": row["created_at"].isoformat(),
            "text": row["text"],
        }

        return MessageDomain.from_dict(data)

    async def save(self, message: MessageDomain) -> None:
        """

        :param message:
        :return:
        """
        try:
            # Используем self._conn напрямую
            await self._conn.execute(
                "INSERT INTO messages (id, created_at, text) VALUES ($1, $2, $3)",
                message.id.value,
                message.created_at,
                message.text.value,
            )
        except asyncpg.exceptions.UniqueViolationError as e:
            raise MessageError(
                f"Message with id {message.id.value} already exists"
            ) from e


def create_asyncpg_message_repository(
    conn: asyncpg.Connection,
) -> AsyncpgMessageRepository:
    """
    Простая фабрика для создания репозитория.
    """
    return AsyncpgMessageRepository(conn=conn)
