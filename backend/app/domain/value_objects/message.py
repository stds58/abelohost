"""
Value Objects для домена Message.
"""

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from ..exceptions.message import EmptyTextError, MessageIDTypeError, MessageIDValueError


@dataclass(frozen=True)
class MessageId:
    """Value Object для идентификатора сообщения (UUID).

    Attributes:
        value: Объект UUID.
    """

    value: UUID

    @classmethod
    def from_str(cls, s: str) -> "MessageId":
        """Создает MessageId из строки.

        Args:
            s: Строковое представление UUID.

        Returns:
            MessageId: Новый экземпляр.

        Raises:
            MessageIDTypeError: Если передан не str.
            MessageIDValueError: Если строка не является валидным UUID.
        """
        if not isinstance(s, str):
            raise MessageIDTypeError
        try:
            return cls(UUID(s))
        except ValueError as err:
            raise MessageIDValueError from err

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Интеграция c Pydantic для валидации входных данных.

        Pydatic сначала парсит как строку, потом вызывает from_str.

        Args:
            _source_type: Тип источника.
            _handler: Обработчик схемы.

        Returns:
            CoreSchema: Схема валидации Pydantic.
        """
        return core_schema.no_info_after_validator_function(
            cls.from_str,
            core_schema.str_schema(),
        )


@dataclass(frozen=True)
class Text:
    """ "Value Object для текста сообщения.

    Attributes:
        value: Строка текста.
    """

    value: str

    def __post_init__(self):
        """Валидирует текст при создании.

        Raises:
            EmptyTextError: Если текст пустой или состоит только из пробелов.
        """
        if not self.value or not self.value.strip():
            raise EmptyTextError
