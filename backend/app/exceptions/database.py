class DatabaseError(Exception):
    """Базовое исключение для ошибок базы данных."""


class DatabaseConnectionError(DatabaseError):
    """Ошибка подключения к БД или критический сбой соединения."""


class DatabaseSchemaError(DatabaseError):
    """Ошибка схемы БД (например, таблица не найдена)."""


class DatabaseTransactionError(DatabaseError):
    """Ошибка транзакции (deadlock, serialization failure)."""


class IntegrityErrorException(DatabaseError):
    """Нарушение ограничений целостности БД (например, уникальность, внешний ключ)."""


class DatabaseConnectionException(DatabaseError):
    """Проблемы c подключением к БД."""


class SqlalchemyErrorException(DatabaseError):
    """Общая ошибка SQLAlchemy."""
