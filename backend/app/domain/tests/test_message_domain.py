"""
Unit-тесты для доменного слоя Message.
"""

from uuid import uuid4

import pytest

from backend.app.domain.entities.message import Message
from backend.app.domain.exceptions.message import (
    EmptyTextError,
    MessageIDTypeError,
    MessageIDValueError,
)
from backend.app.domain.value_objects.message import MessageId


class TestMessageDomain:
    """Комплексные тесты доменного слоя Message.
    Проверяем сущность, валидацию значений и сериализацию.
    """

    def _get_valid_uuid_str(self) -> str:
        """Генерирует валидную строку UUID для тестов.

        Returns:
            str: Строковое представление UUID v4.
        """
        return str(uuid4())

    def test_create_message_success(self):
        """Тест успешного создания сообщения c валидными данными."""
        msg_id_str = self._get_valid_uuid_str()
        text_content = "Hello, World!"

        msg = Message.create(
            message_id=MessageId.from_str(msg_id_str), text=text_content
        )

        assert msg.text.value == text_content
        assert str(msg.id.value) == msg_id_str
        assert msg.created_at is not None
        assert msg.created_at.tzinfo is not None

    def test_message_immutability(self):
        """Тест неизменяемости (frozen) доменной сущности."""
        from dataclasses import FrozenInstanceError

        msg = Message.create(
            message_id=MessageId.from_str(self._get_valid_uuid_str()), text="Immutable"
        )

        print(f"\n[DEBUG] msg.text до изменения: {msg.text}")

        with pytest.raises(FrozenInstanceError):
            msg.text = "Changed"  # type: ignore[misc]
            print(f"[DEBUG] Попытка изменения: {msg.text}")

        print(f"[DEBUG] Если бы не исключение, было бы: {msg.text}")

    def test_serialization_round_trip(self):
        """Тест цикла сериализации: Объект -> JSON -> Объект." """
        original_msg = Message.create(
            message_id=MessageId.from_str(self._get_valid_uuid_str()),
            text="Serialize me",
        )

        json_bytes = original_msg.to_json()
        assert isinstance(json_bytes, bytes)

        restored_msg = Message.from_json(json_bytes)

        assert restored_msg.id == original_msg.id
        assert restored_msg.text == original_msg.text
        assert restored_msg.created_at == original_msg.created_at

    def test_reject_empty_text(self):
        """Тест отвержения пустой строки."""
        with pytest.raises(EmptyTextError):
            Message.create(
                message_id=MessageId.from_str(self._get_valid_uuid_str()), text=""
            )

    def test_reject_whitespace_only_text(self):
        """Тест отвержения строки из пробелов."""
        with pytest.raises(EmptyTextError):
            Message.create(
                message_id=MessageId.from_str(self._get_valid_uuid_str()), text="   "
            )

    def test_reject_invalid_uuid_format(self):
        """Тест отвержения невалидного формата UUID."""
        with pytest.raises(MessageIDValueError):
            Message.create(
                message_id=MessageId.from_str("this-is-not-uuid"), text="Valid text"
            )

    def test_reject_non_string_id_type(self):
        """Тест отвержения не-string типа для ID."""
        with pytest.raises(MessageIDTypeError):
            MessageId.from_str(123)  # type: ignore

    def test_reject_none_text(self):
        """Тест отвержения None вместо текста."""
        with pytest.raises(EmptyTextError):
            Message.create(
                message_id=MessageId.from_str(self._get_valid_uuid_str()),
                text=None,  # type: ignore
            )
