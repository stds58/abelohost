from contextlib import asynccontextmanager

import asyncpg
from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.logging_config import logger as structlog_logger
from backend.app.db.asyncpg_pool import asyncpg_db_client
from backend.app.db.deps import (
    connection_asyncpg_dependency,
    connection_sqlalchemy_dependency,
)
from backend.app.infra.kafka.kafka_producer import kafka_log_producer
from backend.app.middleware.logging import structlog_middleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    structlog_logger.info(
        "application_startup_started",
        workers=settings.GRANIAN_WORKERS,
        debug_mode=settings.DEBUG_MODE,
    )

    try:
        await asyncpg_db_client.connect(
            dsn=settings.DATABASE_URL_FOR_ASYNCPG, min_size=10, max_size=80
        )
        structlog_logger.info("database_connected", pool_min=10, pool_max=80)
    except Exception as e:
        structlog_logger.critical("database_connection_failed", error=str(e))
        raise SystemExit(1) from e

    try:
        kafka_log_producer.start()
        structlog_logger.info("kafka_producer_initialized")
    except Exception as e:
        structlog_logger.critical("kafka_initialization_failed", error=str(e))
        raise SystemExit(1) from e

    yield

    structlog_logger.info("application_shutdown_started")

    kafka_log_producer.stop()
    await asyncpg_db_client.disconnect()
    structlog_logger.info("application_stopped")


app = FastAPI(
    debug=True,
    lifespan=lifespan,
    title="API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


app.middleware("http")(structlog_middleware)

Instrumentator().instrument(app).expose(app, endpoint="/metrics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=False,
    allow_methods=[
        "GET",
        "POST",
        "DELETE",
        "PATCH",
    ],
    allow_headers=[
        "Content-Type",
        "Authorization",
    ],
)

app.include_router(api_router)


@app.get("/health", status_code=status.HTTP_200_OK)
def healthcheck():
    """
    проверка доступности сервиса
    :return:
    """
    structlog_logger.debug("healthcheck_requested")
    return {"status": "healthy", "DM": settings.DEBUG_MODE}


@app.get("/check_sqlalchemy_db-info")
async def get_db_info(
    session: AsyncSession = Depends(connection_sqlalchemy_dependency(commit=False)),
):
    """
    Возвращает информацию o текущем подключении к БД.
    Использует сырую SQL-функцию PostgreSQL.
    для теста ошибки result = await session.execute("SELECT CURRENT_USER, VERSION(), NOW()")
    """
    result = await session.execute(text("SELECT CURRENT_USER, VERSION(), NOW()"))
    row = result.fetchone()
    if row:
        current_user, version, now = row
        return {
            "db_user": current_user,
            "db_version": version,
            "current_time": now.isoformat(),
        }
    return {"error": "No data"}


@app.get("/check_asyncpg_db-info")
async def get_db_info_asyncpg(
    conn: asyncpg.Connection = Depends(connection_asyncpg_dependency()),
):
    """
    Возвращает информацию o текущем подключении к БД через asyncpg.
    """
    row = await conn.fetchrow("SELECT CURRENT_USER, VERSION(), NOW()")

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


if __name__ == "__main__":
    # локальный запуск
    # python backend/app/main.py
    import os
    import subprocess
    import sys

    cmd = [
        "granian",
        "--interface",
        "asgi",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--workers",
        "1",
        "--reload",
        "--access-log",
        "--access-log-fmt",
        '[%(time)s] %(addr)s - "%(method)s %(path)s" %(status)d',
        "backend.app.main:app",
    ]

    try:
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        subprocess.run(cmd, check=True, env=env)
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")  # noqa: RUF001
    except subprocess.CalledProcessError as e:
        print(f"Ошибка запуска Granian: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(
            "Ошибка: granian не найден. Убедитесь, что вы активировали виртуальное окружение и установили зависимости.",
            file=sys.stderr,
        )
        sys.exit(1)
