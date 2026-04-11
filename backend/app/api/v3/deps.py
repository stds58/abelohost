"""
Зависимости (Dependencies) для внедрения репозиториев в эндпоинты
"""

from backend.app.application.repositories.message import MessageRepository
from backend.app.infra.adapters.in_memory_message_repository import (
    in_memory_message_repository_instance,
)


def get_in_memory_repository() -> MessageRepository:
    """Получает репозиторий в памяти (для тестов).

    Returns:
        MessageRepository: Синглтон экземпляра InMemoryMessageRepository.
    """
    return in_memory_message_repository_instance
