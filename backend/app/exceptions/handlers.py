"""
Маппинг доменных ошибок на коды ответов HTTP.
"""

import inspect
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.core.logging_config import logger as structlog_logger
from backend.app.domain.exceptions.message import (
    EmptyTextError,
    MessageDoesNotExistError,
    MessageError,
    MessageIDTypeError,
    MessageIDValueError,
    MessageNotFoundError,
)
from backend.app.exceptions.database import (
    DatabaseConnectionError,
    DatabaseConnectionException,
    DatabaseError,
    DatabaseSchemaError,
    DatabaseTransactionError,
    IntegrityErrorException,
    SqlalchemyErrorException,
)
from backend.app.exceptions.http_exceptions import (
    DatabaseConnectionHTTPException,
    DatabaseHTTPError,
    EmptyTextHTTPError,
    IntegrityErrorHTTPException,
    MessageDoesNotExistHTTPError,
    MessageHTTPError,
    MessageIDTypeHTTPError,
    MessageIDValueHTTPError,
    MessageNotFoundHTTPError,
    SqlalchemyErrorHTTPException,
)

DOMAIN_TO_HTTP_EXCEPTION: dict[type[Exception], type[Exception]] = {
    MessageError: MessageHTTPError,
    MessageNotFoundError: MessageNotFoundHTTPError,
    MessageDoesNotExistError: MessageDoesNotExistHTTPError,
    EmptyTextError: EmptyTextHTTPError,
    MessageIDTypeError: MessageIDTypeHTTPError,
    MessageIDValueError: MessageIDValueHTTPError,
    DatabaseError: DatabaseHTTPError,
    DatabaseConnectionError: DatabaseHTTPError,
    DatabaseSchemaError: DatabaseHTTPError,
    DatabaseTransactionError: DatabaseHTTPError,
    IntegrityErrorException: IntegrityErrorHTTPException,
    DatabaseConnectionException: DatabaseConnectionHTTPException,
    SqlalchemyErrorException: SqlalchemyErrorHTTPException,
}


def make_exception_handler(http_exc_class: type[Exception]) -> Callable:
    """
    Фабрика для создания обработчиков исключений.
    """

    sig = inspect.signature(http_exc_class.__init__)
    target_args = [
        p.name
        for p in sig.parameters.values()
        if p.name not in ("self", "args", "kwargs", "detail", "status_code")
    ]

    async def handler(request: Request, exc: Exception) -> JSONResponse:
        payload = {arg: getattr(exc, arg) for arg in target_args if hasattr(exc, arg)}

        structlog_logger.error(
            "domain_exception_occurred",
            exc_typess=type(
                exc
            ).__name__,  # Название класса (например, MessageNotFound)
            detail=str(exc),  # Сообщение ошибки
            path=request.url.path,  # Куда стучались
            method=request.method,  # Метод запроса
            **payload,  # Распаковка (message_id и прочее)
        )

        http_exc = http_exc_class(**payload)
        return JSONResponse(
            status_code=getattr(http_exc, "status_code", 400),
            content={"detail": getattr(http_exc, "detail", str(exc))},
        )

    return handler


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует все обработчики из маппинга."""
    for domain_exc_class, http_exc_class in DOMAIN_TO_HTTP_EXCEPTION.items():
        app.exception_handler(domain_exc_class)(make_exception_handler(http_exc_class))
