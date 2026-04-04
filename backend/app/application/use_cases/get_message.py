from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message
from backend.app.domain.exceptions.message import MessageDoesNotExistError
from backend.app.domain.value_objects.message import MessageId


class GetMessageUseCase:
    """
    Сценарий: Получить сообщение по идентификатору.

    Отвечает за оркестрацию:
    1. Валидация входного ID (преобразование в Value Object)
    2. Запрос к репозиторию
    3. Обработка случая "не найдено"
    """

    def __init__(self, repository: MessageRepository):
        self._repository = repository

    async def execute(self, message_id: str) -> Message:
        """
        Выполняет сценарий получения сообщения.

        Args:
            message_id: Строковое представление UUID (приходит из API)

        Returns:
            Message: Доменная сущность сообщения

        Raises:
            MessageIDValueError: Если формат ID невалиден
            MessageDoesNotExistError: Если сообщение не найдено в БД
        """
        # 1. Преобразуем строку в доменный Value Object
        # Если формат неверный — вылетит исключение из домена
        id_vo = MessageId.from_str(message_id)

        # 2. Запрашиваем данные через интерфейс репозитория
        message = await self._repository.get_by_id(id_vo)

        # 3. Обрабатываем результат
        if message is None:
            raise MessageDoesNotExistError(f"Message with id {message_id} not found")

        # 4. Возвращаем доменную сущность (или DTO, если нужно скрыть детали)
        return message
