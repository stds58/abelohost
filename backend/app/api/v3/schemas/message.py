"""
Pydantic схемы для API сообщений
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProcessRequest(BaseModel):
    """Схема запроса для создания/обработки сообщения.

    Attributes:
        data: Текстовые данные для обработки.
    """

    data: str


class MessageResponse(BaseModel):
    """Схема ответа c сообщением.

    Attributes:
        id: Уникальный идентификатор сообщения.
        text: Текст сообщения.
        created_at: Дата и время создания.
    """

    id: UUID
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_domain(cls, message) -> "MessageResponse":
        """Фабричный метод для создания DTO из доменной сущности.

        Args:
            message: Доменная сущность Message.

        Returns:
            MessageResponse: Pydantic модель для ответа API.
        """
        return cls(
            id=message.id.value, text=message.text.value, created_at=message.created_at
        )
