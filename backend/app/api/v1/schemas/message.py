from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Импортируем наш Value Object, чтобы Pydantic знал, какего валидировать
# благодаря методу __get_pydantic_core_schema__ в классе MessageId


class MessageCreateRequest(BaseModel):
    """Схема для создания сообщения (POST /message)"""

    model_config = ConfigDict(json_schema_extra={"examples": [{"text": "some text"}]})

    text: str = Field(..., min_length=1, max_length=5000, description="Текст сообщения")


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
