"""
Класс настроек приложения
"""

from functools import lru_cache
from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


def _read_secret_file(file_path: str) -> str:
    """
    Читает секрет из файла, если путь указан
    Args:
        file_path: Путь к файлу c секретом.

    Returns:
        str: Содержимое файла без лишних пробелов.

    Raises:
        RuntimeError: Если файл по указанному пути не найден.
    """
    if not file_path:
        return ""
    try:
        with Path(file_path).open("r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError as err:
        raise RuntimeError(f"Secret file not found: {file_path}") from err


class Settings(BaseSettings):
    """
    берёт настройки из .env и секретов
    Attributes:
        DEBUG_MODE: Режим отладки.
        SECRET_KEY_FILE: Путь к файлу c секретным ключом.
        SESSION_MIDDLEWARE_SECRET_KEY_FILE: Путь к файлу c ключом для middleware сессий.
        GRANIAN_WORKERS: Количество воркеров Granian.
        POSTGRES_USER: Пользователь PostgreSQL.
        POSTGRES_PASSWORD_FILE: Путь к файлу c паролем PostgreSQL.
        POSTGRES_DB: Имя базы данных PostgreSQL.
    """

    # app
    DEBUG_MODE: bool
    SECRET_KEY_FILE: str = ""
    SESSION_MIDDLEWARE_SECRET_KEY_FILE: str = ""
    GRANIAN_WORKERS: int

    # db
    POSTGRES_USER: str
    POSTGRES_PASSWORD_FILE: str = ""
    POSTGRES_DB: str

    @property
    def SECRET_KEY(self) -> str:  # pylint: disable=invalid-name
        """Возвращает секретный ключ, прочитанный из файла.

        Returns:
            str: Секретный ключ.
        """
        return _read_secret_file(self.SECRET_KEY_FILE)

    @property
    def SESSION_MIDDLEWARE_SECRET_KEY(self) -> str:  # pylint: disable=invalid-name
        """Возвращает ключ для middleware сессий, прочитанный из файла.

        Returns:
            str: Ключ для middleware сессий.
        """
        return _read_secret_file(self.SESSION_MIDDLEWARE_SECRET_KEY_FILE)

    @property
    def POSTGRES_PASSWORD(self) -> str:  # pylint: disable=invalid-name
        """Возвращает пароль PostgreSQL, прочитанный из файла.

        Returns:
            str: Пароль PostgreSQL.
        """
        return _read_secret_file(self.POSTGRES_PASSWORD_FILE)

    @property
    def DB_HOST(self):  # pylint: disable=invalid-name
        """Возвращает хост базы данных.
        Note:
            Жестко задан как 'abelo-db' для работы внутри Docker Compose сети.

        Returns:
            str: Хост базы данных.
        """
        return "abelo-db"

    @property
    def DATABASE_URL(self) -> str:  # pylint: disable=invalid-name
        """Формирует URL подключения для SQLAlchemy (asyncpg).

        Returns:
            str: URL подключения вида postgresql+asyncpg://...
        """
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DB_HOST}:5432/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_FOR_ASYNCPG(self) -> str:  # pylint: disable=invalid-name
        """Формирует URL подключения для прямого использования asyncpg.

        Note:
            Отличается от DATABASE_URL отсутствием префикса драйвера в схеме URL,
            так как asyncpg принимает чистый PostgreSQL URL.

        Returns:
            str: URL подключения вида postgresql://...
        """
        return (
            f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
            f"{self.DB_HOST}:5432/{self.POSTGRES_DB}"
        )

    @property
    def DB_POOL_SIZE(self) -> int:  # pylint: disable=invalid-name
        """Рассчитывает размер пула соединений для каждого воркера.

        Note:
            Базируется на общем лимите в 100 соединений, распределенном между воркерами.
            Используется коэффициент 0.8 для основного пула.

        Returns:
            int: Размер пула соединений.

        """
        connects_in_worker = 100 // self.GRANIAN_WORKERS
        _pool_size = round(connects_in_worker * 0.8)
        return _pool_size

    @property
    def DB_MAX_OVERFLOW(self) -> int:  # pylint: disable=invalid-name
        """Рассчитывает максимальное количество дополнительных соединений (overflow).

        Note:
            Это соединения, которые создаются сверх pool_size при высокой нагрузке.

        Returns:
            int: Количество соединений overflow.

        """
        connects_in_worker = 100 // self.GRANIAN_WORKERS
        _max_overflow = connects_in_worker - self.DB_POOL_SIZE
        return _max_overflow

    model_config = ConfigDict(extra="ignore")


@lru_cache
def get_settings():
    """Кеширует экземпляр объекта настроек Settings.

    Предотвращает повторную инициализацию и чтение файлов секретов при каждом импорте.

    Returns:
        Settings: Экземпляр настроек.
    """
    return Settings()


settings = get_settings()
