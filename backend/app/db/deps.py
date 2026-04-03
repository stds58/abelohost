from collections.abc import AsyncGenerator

from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# from backend.app.exceptions.base import CustomInternalServerException
# from backend.app.exceptions.db import (
#     DatabaseConnectionException,
#     IntegrityErrorException,
#     SqlalchemyErrorException,
# )
from backend.app.core.config import settings
from backend.app.db.session import (
    create_session_factory,
    get_session_with_isolation,
)

async_session_maker = create_session_factory(settings.DATABASE_URL)


def connection(commit: bool = True):
    """
    # Фабрика зависимости для FastAPI, создающая асинхронную сессию
    """

    async def dependency() -> AsyncGenerator[AsyncSession]:
        async with get_session_with_isolation(async_session_maker) as session:
            try:
                yield session
                if commit and session.in_transaction():
                    await session.commit()
            except IntegrityError as exc:
                if session.in_transaction():
                    await session.rollback()
                raise #IntegrityErrorException(detail=str(exc)) from exc
            except OperationalError as exc:
                raise #DatabaseConnectionException(detail=str(exc)) from exc
            except (ConnectionRefusedError, OSError) as exc:
                raise #CustomInternalServerException(detail=str(exc)) from exc
            except SQLAlchemyError as exc:
                if session.in_transaction():
                    await session.rollback()
                raise #SqlalchemyErrorException(detail=str(exc)) from exc
            except Exception:
                if session.in_transaction():
                    await session.rollback()
                raise

    return dependency

