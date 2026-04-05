import orjson
from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.app.api.v1.deps import (
    get_sqlalchemy_repository_read,
    get_sqlalchemy_repository_write,
)
from backend.app.api.v1.schemas.message import MessageResponse, ProcessRequest
from backend.app.application.use_cases.create_message import CreateMessageUseCase
from backend.app.application.use_cases.get_message import GetMessageUseCase
from backend.app.domain.exceptions.message import (
    EmptyTextError,
    MessageDoesNotExistError,
    MessageIDValueError,
)

router = APIRouter()


@router.post(
    "/process",
    # response_model=ProcessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Обработать данные c задержкой",
    description="Принимает JSON {data: str}, имитирует обработку (0.5s) и возвращает echo",
)
async def create_message(
    request: ProcessRequest,
    repo: CreateMessageUseCase = Depends(get_sqlalchemy_repository_write),
):
    """
    Принимает текст, создает доменную сущность и сохраняет в БД.
    Симуляция обработки данных c фиксированной задержкой.
    """
    try:
        use_case = CreateMessageUseCase(repository=repo)
        message = await use_case.execute(text=request.data)

        return Response(
            content=orjson.dumps(message.to_dict()), media_type="application/json"
        )

    except EmptyTextError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Текст сообщения не может быть пустым",
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании сообщения: {e!s}",
        ) from e


@router.get(
    "/message/{message_id}",
    response_model=MessageResponse,
    summary="Получить сообщение по ID",
    description="Возвращает сообщение, если оно существует",
)
async def get_message(
    message_id: str,
    repo: GetMessageUseCase = Depends(get_sqlalchemy_repository_read),
):
    """
    Получает сообщение по UUID.
    """
    try:
        use_case = GetMessageUseCase(repository=repo)
        message = await use_case.execute(message_id=message_id)
        return MessageResponse.from_domain(message)

    except MessageIDValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат ID сообщения (ожидается UUID)",
        ) from None
    except MessageDoesNotExistError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Сообщение не найдено {e!s}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении сообщения: {e!s}",
        ) from e
