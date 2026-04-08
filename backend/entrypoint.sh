#!/bin/bash
set -e

# Устанавливаем значение по умолчанию и приводим к нижнему регистру
DEBUG_MODE=${DEBUG_MODE:-true}

# ${DEBUG_MODE,,} — приведение к нижнему регистру
if [ "${DEBUG_MODE,,}" == "true" ]; then
    WORKERS="1"
    CMD_ARGS=(
        --reload
        --access-log
        --access-log-fmt '[%(time)s] %(addr)s - "%(method)s %(path)s" %(status)d'
    )
else
    # === ЗАПУСК МИГРАЦИЙ В ПРОДАКШЕНЕ ===
    echo "[ENTRYPOINT] Running database migrations..."
    # Переходим в директорию backend, так как alembic.ini находится там
    # или указываем путь к нему явно, если нужно.
    # В твоем проекте alembic.ini лежит в backend/
    cd /opt/abelo/backend

    # Запускаем миграции
    # Используем python -m alembic, так как alembic может не быть в PATH напрямую,
    # но он есть в venv, который добавлен в PATH в Dockerfile
    alembic upgrade head

    if [ $? -ne 0 ]; then
        echo "[ENTRYPOINT] ERROR: Migration failed!"
        exit 1
    fi
    echo "[ENTRYPOINT] Migrations completed successfully."

    cd /opt/abelo

    WORKERS=${GRANIAN_WORKERS:-$(nproc)}
    CMD_ARGS=()
fi

exec granian \
    --interface asgi \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "$WORKERS" \
    "${CMD_ARGS[@]}" \
    backend.app.main:app
