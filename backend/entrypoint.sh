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
