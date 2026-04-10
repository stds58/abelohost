"""
Базовые исключения и обработчики для FastAPI приложения.
Использует structlog для консистентного логирования c request_id.
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from backend.app.core.logging_config import logger as structlog_logger


class CustomHTTPException(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"

    def __init__(
        self,
        status_code: int | None = None,
        detail: str | None = None,
    ) -> None:
        final_status = status_code if status_code is not None else self.status_code
        final_detail = detail if detail is not None else self.detail

        super().__init__(status_code=final_status, detail=final_detail)

    async def __call__(self, request: Request, exc: Exception) -> JSONResponse:
        exc_str = str(exc) if str(exc) else exc.__class__.__name__

        structlog_logger.error(
            "http_exception_handled",
            status_code=self.status_code,
            detail=self.detail,
            original_exception_type=exc.__class__.__name__,
            original_exception_msg=exc_str,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            content={"message": self.detail},
            status_code=self.status_code,
        )


class CustomInternalServerException(CustomHTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Внутренняя ошибка сервера"
