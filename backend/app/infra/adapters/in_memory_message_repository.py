"""
In-Memory реализация репозитория сообщений (для тестов)
"""

from uuid import UUID

from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message
from backend.app.domain.value_objects.message import MessageId


class InMemoryMessageRepository(MessageRepository):
    """
    Реализация репозитория, хранящая данные в словаре Python.
    He является потокобезопасной и предназначена только для unit-тестирования.
    """

    def __init__(self):
        self._by_id: dict[UUID, Message] = {}

    async def get_by_id(self, message_id: MessageId) -> Message | None:
        """Получает сообщение из памяти.

        Args:
            message_id: Идентификатор сообщения.

        Returns:
            Message | None: Сообщение или None.
        """
        return self._by_id.get(message_id.value)

    async def save(self, message: Message) -> None:
        """Сохраняет сообщение в память.

        Args:
            message: Сообщение для сохранения.
        """
        self._by_id[message.id.value] = message


in_memory_message_repository_instance = InMemoryMessageRepository()
