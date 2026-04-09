"""
Pydantic схемы для API сообщений
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """Схема запроса для создания/обработки сообщения.

    Attributes:
        data: Текстовые данные для обработки.
    """

    data: str


class ProcessResponse(BaseModel):
    """Схема ответа после обработки данных.

    Attributes:
        processed: Флаг успешной обработки.
        echo: Исходные данные (echo).
        length: Длина исходных данных.
    """

    processed: bool = Field(..., examples=[True])
    echo: str = Field(..., examples=["test data"])
    length: int = Field(..., examples=[9])


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
