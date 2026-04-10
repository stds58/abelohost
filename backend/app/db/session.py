"""
Контекстный менеджер для создания сессии
"""

from contextlib import asynccontextmanager

# import structlog
# from app.core.async_logger import ainfo, aerror, awarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.app.core.config import settings

# logger = structlog.get_logger()


def create_session_factory(database_url: str):
    """Создает фабрику сессий для заданного URL базы данных.

    Args:
        database_url: URL подключения к базе данных.

    Returns:
        async_sessionmaker: Фабрика для создания асинхронных сессий.

    Notes:
        pool_size количество соединений в пуле
        max_overflow количество "переполненных" соединений
    """
    engine = create_async_engine(
        database_url,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        echo=False,
        connect_args={
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        },
    )
    return async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def get_session(session_factory):
    """
    Асинхронный контекстный менеджер для получения сессии.

    Args:
        session_factory: Фабрика для создания асинхронной сессии.

    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.

    Raises:
        ConnectionRefusedError: Если не удалось подключиться к БД.
        OSError: Если произошла системная ошибка.
        asyncio.TimeoutError: Если истекло время ожидания подключения.
    """
    try:
        async with session_factory() as session:
            yield session
    except (TimeoutError, ConnectionRefusedError, OSError):
        raise
