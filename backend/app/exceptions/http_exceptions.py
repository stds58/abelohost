"""
HTTP-исключения приложения.
"""

from fastapi import status

from backend.app.exceptions.base import CustomHTTPException


class BaseAPIException(CustomHTTPException):
    """Базовый класс для всех кастомных HTTP-исключений приложения."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class MessageHTTPError(BaseAPIException):
    """Ошибки домена Message"""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class MessageNotFoundHTTPError(MessageHTTPError):
    """404: Сообщение не найдено (общая ошибка)."""

    def __init__(self, detail: str = "Message not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# pylint: disable=too-many-ancestors
class MessageDoesNotExistHTTPError(MessageNotFoundHTTPError):
    """404: Сообщение не найдено."""

    def __init__(self, message_id: str | None = None):
        if message_id:
            detail = f"Message with id '{message_id}' not found"
        else:
            detail = "Message not found"

        super().__init__(detail=detail)


class EmptyTextHTTPError(MessageHTTPError):
    """400: Пустой текст сообщения."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message text cannot be empty or whitespace only",
        )


class MessageIDTypeHTTPError(MessageHTTPError):
    """422: Неверный тип данных ID."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message ID must be a string",
        )


class MessageIDValueHTTPError(MessageHTTPError):
    """
    400: Неверный формат ID сообщения.
    Возвращается, если переданный ID не является валидным UUID.
    """

    def __init__(self, invalid_id: str | None = None):
        detail = "Invalid message ID format. Expected UUID."
        if invalid_id:
            detail = f"Invalid message ID format: '{invalid_id}'. Expected UUID."
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class DatabaseHTTPError(BaseAPIException):
    """500: Внутренняя ошибка базы данных."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class IntegrityErrorHTTPException(DatabaseHTTPError):
    """409: Нарушение ограничений целостности БД (например, уникальность, внешний ключ)."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, detail="Нарушение целостности данных"
        )


class DatabaseConnectionHTTPException(DatabaseHTTPError):
    """503: Проблемы c подключением к БД."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис базы данных временно недоступен",
        )


class SqlalchemyErrorHTTPException(DatabaseHTTPError):
    """500: Общая ошибка SQLAlchemy."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных",
        )
