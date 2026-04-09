"""
Use case для получения сообщения по идентификатору.
"""

from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message
from backend.app.domain.exceptions.message import MessageDoesNotExistError
from backend.app.domain.value_objects.message import MessageId


class GetMessageUseCase:
    """Сценарий использования для получения сообщения по идентификатору.

    Отвечает за оркестрацию бизнес-логики:
    1. Валидация входного ID (преобразование строки в Value Object MessageId).
    2. Запрос данных через репозиторий.
    3. Обработка случая, когда сообщение не найдено.

    Attributes:
        _repository: Экземпляр репозитория для доступа к данным.
    """

    def __init__(self, repository: MessageRepository):
        """Инициализирует UseCase c переданным репозиторием.

        Args:
            repository: Реализация интерфейса MessageRepository.
        """
        self._repository = repository

    async def execute(self, message_id: str) -> Message:
        """Выполняет сценарий получения сообщения.

        Преобразует строковый идентификатор в Value Object, запрашивает
        сообщение из репозитория и возвращает доменную сущность.

        Args:
            message_id: Строковое представление UUID сообщения.

        Returns:
            Message: Доменная сущность сообщения.

        Raises:
            MessageIDValueError: Если формат ID невалиден (ошибка преобразования в VO).
            MessageDoesNotExistError: Если сообщение c таким ID не найдено в БД.
        """
        id_vo = MessageId.from_str(message_id)
        message = await self._repository.get_by_id(id_vo)

        if message is None:
            raise MessageDoesNotExistError(f"Message with id {message_id} not found")

        return message
