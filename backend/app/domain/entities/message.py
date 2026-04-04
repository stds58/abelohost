from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import orjson

from ..value_objects.message import MessageId, Text


# pylint: disable=too-many-instance-attributes
@dataclass(frozen=True)
class Message:
    """
    Доменная сущность сообщения
    """

    id: MessageId
    """Уникальный идентификатор сообщения"""

    created_at: datetime
    """Дата и время создания записи (UTC)"""

    text: Text
    """ """

    @classmethod
    def create(
        cls,
        *,
        message_id: MessageId,
        text: str,
    ) -> "Message":
        """
        Фабричный метод для создания нового сообщения.
        Args:
        Returns:
        """
        return cls(
            id=message_id,
            created_at=datetime.now(UTC),
            text=Text(value=text),
        )

    def to_dict(self) -> dict[str, Any]:
        """Преобразует сущность сообщения в словарь для последующей сериализации.

        Извлекает значения из Value Objects
        и преобразует datetime в ISO-8601 формат для совместимости c JSON.

        Returns:
            Dict[str, Any]: Словарь c сериализуемыми данными пользователя. Bce
                Value Objects представлены своими базовыми значениями (str, int).
                Поля c None остаются None.

        Example:
            >>> message = Message(...)
            >>> data = message.to_dict()
            >>> data["text"]
        """
        return {
            "id": self.id.value,
            "created_at": self.created_at.isoformat(),
            "text": self.text.value,
        }

    def to_json(self) -> bytes:
        """Сериализует сущность User в JSON-формат используя orjson.

        Преобразует словарь данных (полученный через to_dict) в бинарный JSON.
        Bce даты автоматически форматируются в UTC c суффиксом 'Z' благодаря
        флагу OPT_UTC_Z.

        Returns:
            bytes: Байтовое представление JSON. Готово для записи в Redis,
                Kafka или PostgreSQL JSONB.

        Note:
            Метод синхронный и выполняется крайне быстро. Исключения возможны
            только в случае критической ошибки программирования внутри to_dict(),
            если там останутся неподдерживаемые типы данных.

        Example:
            >>> data = message.to_json()
            >>> isinstance(data, bytes)
            True
        """
        # pylint: disable=no-member
        return orjson.dumps(
            self.to_dict(),
            option=orjson.OPT_SERIALIZE_DATACLASS | orjson.OPT_UTC_Z,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """Восстанавливает сущность Message из словаря данных.

        Преобразует сырые значения (str, int, bool) обратно в Value Objects
        (MessageId) и парсит ISO-8601 строки в datetime.
        Используется после загрузки данных из базы данных или кэша.

        Args:
            data (Dict[str, Any]): Словарь c данными пользователя. Должен
                содержать все обязательные поля: id, created_at, email,
                display_name, hash_password. Опциональные поля могут быть None.

        Returns:
            Message: Новый неизменяемый экземпляр сущности User c восстановленными
                Value Objects и корректными типами данных.

        Raises:
            ValueError: Если формат даты не соответствует ISO-8601.
            KeyError: Если отсутствует обязательное поле в словаре данных.

        Example:
            >>> data = {"id": "msg_123", "text": "some text", ...}
            >>> message = Message.from_dict(data)
            >>> message.text
        """

        restored_id = MessageId.from_str(data["id"])
        restored_text = Text(value=data["text"])

        created_at_str = data["created_at"]
        created_at = datetime.fromisoformat(created_at_str).astimezone(UTC)

        return cls(
            id=restored_id,
            created_at=created_at,
            text=restored_text,
        )

    @classmethod
    def from_json(cls, json_bytes: bytes) -> "Message":
        """Восстанавливает сущность Message из JSON-байтов используя orjson.

        Обратная операция к to_json(). Десериализует бинарные JSON-данные
        и создаёт экземпляр сущности через from_dict(). Используется для
        загрузки из кэша, очереди сообщений или JSONB-поля БД.

        Args:
            json_bytes (bytes): JSON-представление пользователя в бинарном
                формате. Должно быть корректным JSON, полученным из to_json()
                или совместимого источника.

        Returns:
            User: Новый неизменяемый экземпляр сущности User c восстановленными
                данными и Value Objects.

        Raises:
            orjson.JSONDecodeError: Если входные данные не являются валидным JSON.
            ValueError: Если формат данных не соответствует ожидаемой структуре.
            KeyError: Если в JSON отсутствует обязательное поле.

        Example:
            >>> json_bytes = redis_client.get(f"user:{message_id}")
            >>> message = Message.from_json(json_bytes)
            >>> message.text
            True
        """
        # pylint: disable=no-member
        data = orjson.loads(json_bytes)
        return cls.from_dict(data)
