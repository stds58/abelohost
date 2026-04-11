"""
Сценарий использования для создания нового сообщения.
"""

from uuid_extensions import uuid7

from backend.app.application.repositories.message import MessageRepository
from backend.app.core.logging_config import logger as structlog_logger
from backend.app.domain.entities.message import Message
from backend.app.domain.value_objects.message import MessageId


class CreateMessageUseCase:
    """Use case для создания нового сообщения c симуляцией обработки.

    Отвечает за оркестрацию процесса создания:
    1. Генерация уникального идентификатора (UUID7).
    2. Создание доменной сущности через фабричный метод.
    3. Сохранение сущности через репозиторий.

    Attributes:
        _repository: Экземпляр репозитория для сохранения данных.
    """

    def __init__(self, repository: MessageRepository):
        """Инициализирует UseCase c переданным репозиторием.

        Args:
            repository: Реализация интерфейса MessageRepository.
        """
        self._repository = repository

    async def execute(self, text: str) -> Message:
        """
        Выполняет сценарий создания сообщения.

        Args:
            text: Текст сообщения

        Returns:
            Message: Созданная доменная сущность сообщения c ID и timestamp.

        Raises:
            EmptyTextError: Если текст пустой или содержит только пробелы
            MessageError: Если сообщение c таким ID уже существует (маловероятно для uuid7)
        """

        new_id = MessageId.from_str(str(uuid7()))
        message = Message.create(message_id=new_id, text=text)
        await self._repository.save(message)
        structlog_logger.info("use cases create_message", message_id=message.id.value)
        return message
