from abc import ABC, abstractmethod

from backend.app.domain.entities.message import Message
from backend.app.domain.value_objects.message import MessageId


class MessageRepository(ABC):
    @abstractmethod
    async def get_by_id(self, message_id: MessageId) -> Message | None: ...

    @abstractmethod
    async def save(self, message: Message) -> None: ...
