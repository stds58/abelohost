from dataclasses import dataclass
from typing import Any
from uuid import UUID

from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from ..exceptions.message import EmptyTextError, MessageIDTypeError, MessageIDValueError


@dataclass(frozen=True)
class MessageId:
    value: UUID

    @classmethod
    def from_str(cls, s: str) -> "MessageId":
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
        # Pydantic будет сначала парсить как строку, потом вызывать from_str
        return core_schema.no_info_after_validator_function(
            cls.from_str,
            core_schema.str_schema(),
        )


@dataclass(frozen=True)
class Text:
    value: str

    def __post_init__(self):
        if not self.value or not self.value.strip():
            raise EmptyTextError
