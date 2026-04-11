"""
API healthcheck
"""

from fastapi import APIRouter, status

from backend.app.core.logging_config import logger as structlog_logger

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def healthcheck():
    """Проверка доступности сервиса (Healthcheck).

    Returns:
        dict: Статус сервиса и режим отладки.
    """
    structlog_logger.debug("healthcheck_requested")
    return {"status": "healthy"}
