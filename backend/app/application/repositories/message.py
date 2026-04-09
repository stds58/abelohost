"""
Абстрактный интерфейс репозитория сообщений.
"""

from abc import ABC, abstractmethod

from backend.app.domain.entities.message import Message
from backend.app.domain.value_objects.message import MessageId


class MessageRepository(ABC):
    """
    Абстрактный базовый класс для репозиториев сообщений.
    Определяет контракт для сохранения и получения сообщений независимо от реализации БД.
    """

    @abstractmethod
    async def get_by_id(self, message_id: MessageId) -> Message | None:
        """Получает сообщение по идентификатору.

        Args:
            message_id: Value Object идентификатора сообщения.

        Returns:
            Message | None: Доменная сущность или None, если не найдено.
        """
        ...

    @abstractmethod
    async def save(self, message: Message) -> None:
        """Сохраняет сообщение в хранилище.

        Args:
            message: Доменная сущность сообщения.
        """
        ...
