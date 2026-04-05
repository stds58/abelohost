"""
Контекстный менеджер для создания сессии c опциональным уровнем изоляции.
Для гибкого управления уровнем изоляции
"""

from contextlib import asynccontextmanager

# import structlog
# from app.core.async_logger import ainfo, aerror, awarning
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# logger = structlog.get_logger()


def create_session_factory(database_url: str):
    """Создает фабрику сессий для заданного URL базы данных"""
    engine = create_async_engine(
        database_url,
        pool_size=13,  # 13 количество соединений в пуле
        max_overflow=3,  # 3 количество "переполненных" соединений
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
        # await aerror(
        #     "Ошибка (ConnectionRefusedError, OSError, asyncio.TimeoutError)",
        #     error=str(exc),
        # )
        raise
