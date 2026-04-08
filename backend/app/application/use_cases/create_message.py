import asyncio

from uuid_extensions import uuid7

from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message
from backend.app.domain.value_objects.message import MessageId


class CreateMessageUseCase:
    """
    Сценарий: Создать новое сообщение + Симуляция обработки данных c фиксированной задержкой.

    Отвечает за:
    1. Генерацию уникального идентификатора
    2. Создание доменной сущности через фабричный метод
    3. Сохранение через репозиторий
    """

    def __init__(self, repository: MessageRepository):
        self._repository = repository

    async def execute(self, text: str) -> Message:
        """
        Выполняет сценарий создания сообщения.

        Args:
            text: Текст сообщения (валидируется внутри домена)

        Returns:
            Message: Newly created domain entity with generated ID and timestamp

        Raises:
            EmptyTextError: Если текст пустой или содержит только пробелы
            MessageError: Если сообщение c таким ID уже существует (маловероятно для uuid7)
        """

        # Симуляция latency
        await asyncio.sleep(0.5)

        # 1. Генерируем уникальный ID (uuid7 = время-сортируемый UUID)
        # Можно использовать uuid.uuid4() если не нужна сортировка по времени
        new_id = MessageId.from_str(str(uuid7()))

        # 2. Создаём сущность через фабричный метод домена
        # Здесь сработает валидация текста (пустой? пробелы?)
        # И автоматически проставится created_at
        message = Message.create(message_id=new_id, text=text)

        # 3. Сохраняем через репозиторий
        # Репозиторий выбросит исключение, если нарушена уникальность
        await self._repository.save(message)

        # 4. Возвращаем созданную сущность
        return message
