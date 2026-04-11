""" """

import asyncpg
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.logging_config import logger as structlog_logger
from backend.app.db.deps import (
    connection_asyncpg_dependency,
    connection_sqlalchemy_dependency,
)

router = APIRouter()


@router.get("/check_sqlalchemy_db-info")
async def get_db_info(
    session: AsyncSession = Depends(connection_sqlalchemy_dependency(commit=False)),
):
    """Возвращает информацию o текущем подключении к БД через SQLAlchemy.
    Использует сырую SQL-функцию PostgreSQL для проверки соединения.

    Args:
        session: Сессия SQLAlchemy.

    Returns:
        dict: Информация o пользователе, версии БД и текущем времени.
    """
    result = await session.execute(text("SELECT CURRENT_USER, VERSION(), NOW()"))
    row = result.fetchone()
    structlog_logger.debug("check_sqlalchemy_db-info_requested")
    if row:
        current_user, version, now = row
        return {
            "db_user": current_user,
            "db_version": version,
            "current_time": now.isoformat(),
        }
    return {"error": "No data"}


@router.get("/check_asyncpg_db-info")
async def get_db_info_asyncpg(
    conn: asyncpg.Connection = Depends(connection_asyncpg_dependency()),
):
    """Возвращает информацию o текущем подключении к БД через asyncpg.

    Args:
        conn: Соединение asyncpg.

    Returns:
        dict: Информация o пользователе, версии БД и текущем времени.
    """
    row = await conn.fetchrow("SELECT CURRENT_USER, VERSION(), NOW()")
    structlog_logger.debug("check_asyncpg_db-info_requested")

    if row:
        current_user = row["current_user"]
        version = row["version"]
        now = row["now"]

        return {
            "db_user": current_user,
            "db_version": version,
            "current_time": now.isoformat(),
        }
    return {"error": "No data"}
