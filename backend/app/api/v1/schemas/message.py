from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """Схема для создания сообщения (POST /message)"""

    data: str


class ProcessResponse(BaseModel):
    processed: bool = Field(..., examples=[True])
    echo: str = Field(..., examples=["test data"])
    length: int = Field(..., examples=[9])


class MessageResponse(BaseModel):
    """Схема ответа c сообщением"""

    id: UUID
    text: str
    created_at: datetime

    class Config:
        from_attributes = (
            True  # Если бы мы маппили ORM напрямую, но тут мы маппим Domain Entity
        )
        # Для domain entity лучше использовать model_validator или просто явное присваивание в endpoint

    @classmethod
    def from_domain(cls, message) -> "MessageResponse":
        """Фабричный метод для создания DTO из доменной сущности"""
        return cls(
            id=message.id.value, text=message.text.value, created_at=message.created_at
        )
