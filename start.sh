#!/bin/bash

# Определяем список файлов массивом для читаемости
COMPOSE_FILES=(
    "docker-compose.yml"
    "docker-compose-grafana.yml"
    "docker-compose-loki.yml"
    "docker-compose-node-exporter.yml"
    "docker-compose-promtail.yml"
    "docker-compose-kafka.yml"
    "docker-compose-alloy.yml"
    "docker-compose-prometheus.yml"
    "docker-compose-wrk.yml"
)

# Собираем строку через разделитель ':'
COMPOSE_FILE_STRING=$(IFS=:; echo "${COMPOSE_FILES[*]}")

# Экспортируем переменные
export COMPOSE_PATH_SEPARATOR=:
export COMPOSE_FILE="$COMPOSE_FILE_STRING"

# Запускаем docker compose с переданными аргументами
docker compose "$@"