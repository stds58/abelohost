from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

# from backend.app.exceptions.base import CustomInternalServerException
# from backend.app.exceptions.db import (
#     DatabaseConnectionException,
#     IntegrityErrorException,
#     SqlalchemyErrorException,
# )
from backend.app.core.config import settings
from backend.app.db.asyncpg_pool import asyncpg_db_client
from backend.app.db.session import create_session_factory, get_session

async_session_maker = create_session_factory(settings.DATABASE_URL)


@asynccontextmanager
async def connection_sqlalchemy(commit: bool = True) -> AsyncGenerator[AsyncSession]:
    async with get_session(async_session_maker) as session:
        try:
            yield session
            if commit and session.in_transaction():
                await session.commit()
        except IntegrityError:
            if session.in_transaction():
                await session.rollback()
            raise  # IntegrityErrorException(detail=str(exc)) from exc
        except OperationalError:
            raise  # DatabaseConnectionException(detail=str(exc)) from exc
        except (ConnectionRefusedError, OSError):
            raise  # CustomInternalServerException(detail=str(exc)) from exc
        except SQLAlchemyError:
            if session.in_transaction():
                await session.rollback()
            raise  # SqlalchemyErrorException(detail=str(exc)) from exc
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise


def connection_sqlalchemy_dependency(commit: bool = True):
    """
    Фабрика зависимости для FastAPI, создающая асинхронную сессию
    """

    async def dependency() -> AsyncGenerator[AsyncSession]:
        async with connection_sqlalchemy(commit=commit) as session:
            yield session

    return dependency


@asynccontextmanager
async def connection_asyncpg() -> AsyncGenerator[asyncpg.Connection]:
    """
    Прямой доступ к asyncpg.Connection c управлением транзакцией.
    """
    async with asyncpg_db_client.get_connection() as conn, conn.transaction():
        yield conn


def connection_asyncpg_dependency():
    """Фабрика зависимости FastAPI для asyncpg connection"""

    async def dependency() -> AsyncGenerator[asyncpg.Connection]:
        async with connection_asyncpg() as conn:
            yield conn

    return dependency
