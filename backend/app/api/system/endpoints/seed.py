"""
Эндпоинт для вставки Mock-данных
"""

from fastapi import APIRouter, Depends, status
from uuid_extensions import uuid7

from backend.app.api.system.deps import get_asyncpg_repository
from backend.app.application.use_cases.create_message import CreateMessageUseCase
from backend.app.core.logging_config import logger as structlog_logger

router = APIRouter()


MOCK_MESSAGES = [
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
    f"Seed message {uuid7()!s}",
]


@router.post(
    "/seed",
    status_code=status.HTTP_201_CREATED,
    summary="Заполнить БД тестовыми данными",
    description="Вставляет фиксированный набор из 10+ сообщений в БД через UseCase.",
)
async def create_seed_message(
    repo=Depends(get_asyncpg_repository),
):
    """Массово создает сообщения для тестирования.

    Args:
        repo: Зависимость UseCase для создания сообщения.

    Returns:
        Response: None

    Raises:
        HTTPException: 400 Bad Request, если текст пустой.
        HTTPException: 500 Internal Server Error при непредвиденных ошибках.
    """
    use_case = CreateMessageUseCase(repository=repo)
    cnt = 0

    for text in MOCK_MESSAGES:
        try:
            await use_case.execute(text=text)
            cnt += 1
        except Exception as e:
            structlog_logger.error("seed_failed", text=text, error=str(e))

    structlog_logger.info("seed_completed", count=cnt, api_version="system asyncpg")

    return {
        "status": "done",
        "count": cnt,
    }
