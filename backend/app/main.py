"""
локальный запуск
python backend/app/main.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from backend.app.api.system.router import api_router as system_router
from backend.app.api.v1.router import api_router as v1_api_router
from backend.app.api.v2.router import api_router as v2_api_router
from backend.app.api.v3.router import api_router as v3_api_router
from backend.app.core.config import settings
from backend.app.core.logging_config import logger as structlog_logger
from backend.app.db.asyncpg_pool import asyncpg_db_client
from backend.app.exceptions.handlers import register_exception_handlers
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

app.include_router(system_router)
app.include_router(v1_api_router)
app.include_router(v2_api_router)
app.include_router(v3_api_router)
register_exception_handlers(app)
if settings.DEBUG_MODE:
    Instrumentator().instrument(app).expose(app)


if __name__ == "__main__":
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
