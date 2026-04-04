"""
Класс настроек приложения
"""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


def _read_secret_file(file_path: str) -> str:
    """Читает секрет из файла, если путь указан"""
    if not file_path:
        return ""
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError as err:
        raise RuntimeError(f"Secret file not found: {file_path}") from err


class Settings(BaseSettings):
    """
    берёт настройки из .env или секретов
    """

    # app
    DEBUG_MODE: bool
    SECRET_KEY_FILE: str = ""
    SESSION_MIDDLEWARE_SECRET_KEY_FILE: str = ""

    # db
    POSTGRES_USER: str
    POSTGRES_PASSWORD_FILE: str = ""
    POSTGRES_DB: str

    @property
    def SECRET_KEY(self) -> str:  # pylint: disable=invalid-name
        return _read_secret_file(self.SECRET_KEY_FILE)

    @property
    def SESSION_MIDDLEWARE_SECRET_KEY(self) -> str:  # pylint: disable=invalid-name
        return _read_secret_file(self.SESSION_MIDDLEWARE_SECRET_KEY_FILE)

    @property
    def POSTGRES_PASSWORD(self) -> str:  # pylint: disable=invalid-name
        return _read_secret_file(self.POSTGRES_PASSWORD_FILE)

    @property
    def DB_HOST(self):  # pylint: disable=invalid-name
        return "abelo-db"

    @property
    def DATABASE_URL(self) -> str:  # pylint: disable=invalid-name
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DB_HOST}:5432/{self.POSTGRES_DB}"
        )

    @property
    def BACKEND_WORKERS(self) -> int:  # pylint: disable=invalid-name
        """количество ядер=количество воркеров граниана"""
        workers = os.cpu_count()
        return workers

    @property
    def DB_POOL_SIZE(self) -> int:  # pylint: disable=invalid-name
        """количество соединений в пуле бд"""
        connects_in_worker = 100 // self.BACKEND_WORKERS
        _pool_size = round(connects_in_worker * 0.8)
        return _pool_size

    @property
    def DB_MAX_OVERFLOW(self) -> int:  # pylint: disable=invalid-name
        """количество "переполненных" соединений в бд"""
        connects_in_worker = 100 // self.BACKEND_WORKERS
        _max_overflow = connects_in_worker - self.DB_POOL_SIZE
        return _max_overflow

    @property
    def NUM_CORES(self) -> int:  # pylint: disable=invalid-name
        return os.cpu_count()

    model_config = ConfigDict(extra="ignore")


@lru_cache
def get_settings():
    """
    кеширует экземпляр объекта настроек Settings, чтобы избежать повторной инициализации
    """
    return Settings()


settings = get_settings()
