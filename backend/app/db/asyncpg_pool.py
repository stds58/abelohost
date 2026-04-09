"""
Управление пулом соединений asyncpg.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg


class AsyncPGDatabase:
    """Класс для управления единственным пулом соединений asyncpg."""

    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self, dsn: str, min_size: int = 10, max_size: int = 80):
        """Инициализирует пул соединений, если он еще не создан.

        Args:
            dsn: Строка подключения к базе данных.
            min_size: Минимальное количество соединений в пуле.
            max_size: Максимальное количество соединений в пуле.
        """
        if self._pool is not None:
            return

        self._pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=min_size,
            max_size=max_size,
            command_timeout=5,
            statement_cache_size=0,
        )

    async def disconnect(self):
        """Закрывает пул соединений и очищает ссылку"""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection]:
        """Предоставляет соединение из пула через контекстный менеджер.

        Yields:
            asyncpg.Connection: Активное соединение c базой данных.

        Raises:
            RuntimeError: Если пул не был инициализирован вызовом connect().
        """
        if self._pool is None:
            raise RuntimeError("Pool not initialized. Call connect() first.")
        async with self._pool.acquire() as conn:
            yield conn


asyncpg_db_client = AsyncPGDatabase()
