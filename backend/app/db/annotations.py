"""
SQLAlchemy аннотации типов для стандартных колонок базы данных.

Содержит переиспользуемые типы для первичных ключей (UUID)
и временных меток создания записей (CreatedAt).
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import TIMESTAMP, UUID as SQLAlchemyUUID, text
from sqlalchemy.orm import mapped_column
from uuid_extensions import uuid7

UUIDPk = Annotated[
    UUID,
    mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
        server_default=None,
    ),
]
"""Аннотированный тип для первичного ключа UUID.

Используется в моделях SQLAlchemy для автоматической генерации UUID v7 на стороне приложения.

Attributes:
    SQLAlchemyUUID(as_uuid=True): Тип колонки UUID, возвращает объект Python UUID.
    primary_key=True: Помечает колонку как первичный ключ.
    default=uuid7: Функция для генерации значения по умолчанию при создании объекта в Python.
    server_default=None: Отсутствие значения по умолчанию на стороне БД (генерация идет в приложении).
"""

CreatedAt = Annotated[
    datetime,
    mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('utc', CURRENT_TIMESTAMP)"),
    ),
]
"""Аннотированный тип для временной метки создания записи.

Используется в моделях SQLAlchemy для автоматической установки времени создания записи
на стороне базы данных при INSERT.

Attributes:
    TIMESTAMP(timezone=True): Тип колонки timestamp c поддержкой часовых поясов.
    server_default: SQL-выражение для установки текущего времени UTC при создании записи.
"""
