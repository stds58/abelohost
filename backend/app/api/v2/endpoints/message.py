"""
Эндпоинты для работы c сообщениями (Message API)
"""

import asyncio

import orjson
from fastapi import APIRouter, Depends, Response, status

from backend.app.api.v2.deps import (
    get_sqlalchemy_repository_read,
    get_sqlalchemy_repository_write,
)
from backend.app.api.v2.schemas.message import ProcessRequest
from backend.app.application.use_cases.create_message import CreateMessageUseCase
from backend.app.application.use_cases.get_message import GetMessageUseCase
from backend.app.core.logging_config import logger as structlog_logger

router = APIRouter()


@router.post(
    "/process",
    status_code=status.HTTP_201_CREATED,
    summary="Обработать данные c задержкой",
    description="Принимает JSON {data: str}, имитирует обработку (0.5s) и возвращает echo",
)
async def create_message(
    request: ProcessRequest,
    repo: CreateMessageUseCase = Depends(get_sqlalchemy_repository_write),
):
    """Принимает текст, создает доменную сущность и сохраняет в БД.
    Симуляция обработки данных c фиксированной задержкой.

    Args:
        request: Тело запроса c полем data (str).
        repo: Зависимость UseCase для создания сообщения.

    Returns:
        Response: JSON-ответ c данными созданного сообщения.

    Raises:
        HTTPException: 400 Bad Request, если текст пустой.
        HTTPException: 500 Internal Server Error при непредвиденных ошибках.
    """
    await asyncio.sleep(0.5)
    use_case = CreateMessageUseCase(repository=repo)
    message = await use_case.execute(text=request.data)
    structlog_logger.info(
        "create_message", message_id=message.id.value, api_version="v2 sqlalchemy"
    )
    return Response(
        content=orjson.dumps(message.to_dict()),
        media_type="application/json",
        status_code=status.HTTP_201_CREATED,
    )


@router.get(
    "/message/{message_id}",
    summary="Получить сообщение по ID",
    description="Возвращает сообщение, если оно существует",
)
async def get_message(
    message_id: str,
    repo: GetMessageUseCase = Depends(get_sqlalchemy_repository_read),
):
    """Получает сообщение по UUID.

    Args:
        message_id: Строковый идентификатор сообщения (UUID).
        repo: Зависимость UseCase для получения сообщения.

    Returns:
        Response: JSON-ответ c данными сообщения.

    Raises:
        HTTPException: 400 Bad Request, если формат ID невалиден.
        HTTPException: 404 Not Found, если сообщение не найдено.
        HTTPException: 500 Internal Server Error при непредвиденных ошибках.
    """
    use_case = GetMessageUseCase(repository=repo)
    message = await use_case.execute(message_id=message_id)
    structlog_logger.info(
        "get_message", message_id=message_id, api_version="v2 sqlalchemy"
    )
    return Response(content=message.to_json(), media_type="application/json")
