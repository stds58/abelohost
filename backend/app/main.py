from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.config import settings
from backend.app.db.deps import connection


app = FastAPI(
    debug=True,
    # lifespan=lifespan,
    title="API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


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



@app.get("/health", status_code=status.HTTP_200_OK)
def healthcheck():
    """
    проверка доступности сервиса
    :return:
    """
    if settings.DEBUG_MODE:
        return {
            "message": "Fastapi is running",
            "DEBUG_MODE": settings.DEBUG_MODE,
        }
    return {"message": "Fastapi is running"}


@app.get("/db-info")
async def get_db_info(
    session: AsyncSession = Depends(connection(commit=False)),
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

