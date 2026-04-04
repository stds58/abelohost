from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.v1.deps import (
    get_create_message_use_case,
    get_get_message_use_case,
)
from backend.app.api.v1.schemas.message import MessageCreateRequest, MessageResponse
from backend.app.application.use_cases.create_message import CreateMessageUseCase
from backend.app.application.use_cases.get_message import GetMessageUseCase
from backend.app.domain.exceptions.message import (
    EmptyTextError,
    MessageDoesNotExistError,
    MessageIDValueError,
)

router = APIRouter()


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новое сообщение",
    description="Создает сообщение c валидацией текста и генерацией UUID7",
)
async def create_message(
    body: MessageCreateRequest,
    use_case: CreateMessageUseCase = Depends(get_create_message_use_case),
):
    """
    Принимает текст, создает доменную сущность и сохраняет в БД.
    """
    try:
        # Execute возвращает доменную сущность Message
        message = await use_case.execute(text=body.text)
        # Конвертируем доменную сущность в DTO для ответа
        return MessageResponse.from_domain(message)

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
    "/{message_id}",
    response_model=MessageResponse,
    summary="Получить сообщение по ID",
    description="Возвращает сообщение, если оно существует",
)
async def get_message(
    message_id: str,
    # Pydantic сам попробует сконвертировать это в MessageId внутри UseCase, но здесь оставляем str для гибкости обработки ошибок URL
    use_case: GetMessageUseCase = Depends(get_get_message_use_case),
):
    """
    Получает сообщение по UUID.
    """
    try:
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
