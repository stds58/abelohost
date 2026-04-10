"""
доменные исключения
"""


class MessageError(Exception):
    """Базовый класс для всех доменных исключений."""


class MessageNotFoundError(MessageError):
    """Сообщение не найдено для выполнения этого действия"""


class MessageDoesNotExistError(MessageNotFoundError):
    """
    Выбрасывается при обращении к сообщению по идентификатору или уникальному атрибуту,
    которого не существует в системе.

    Возникает, когда ожидается наличие сущности, но она не найдена.
    """

    def __init__(self, message_id: str | None = None):
        self.message_id = message_id
        super().__init__(f"Message with id {message_id} not found")


class EmptyTextError(MessageError):
    """Сообщение не может быть пустым"""


class MessageIDTypeError(MessageError):
    """Message ID must be a string"""


class MessageIDValueError(MessageError):
    """Invalid Message ID format"""
