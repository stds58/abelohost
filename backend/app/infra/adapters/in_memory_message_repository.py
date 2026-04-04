from uuid import UUID

from backend.app.application.repositories.message import MessageRepository
from backend.app.domain.entities.message import Message
from backend.app.domain.value_objects.message import MessageId


class InMemoryMessageRepository(MessageRepository):
    def __init__(self):
        self._by_id: dict[UUID, Message] = {}

    async def get_by_id(self, message_id: MessageId) -> Message | None:
        return self._by_id.get(message_id.value)

    async def save(self, message: Message) -> None:
        self._by_id[message.id.value] = message


in_memory_message_repository_instance = InMemoryMessageRepository()
