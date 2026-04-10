#!/bin/bash

COMPOSE_FILES=(
    "docker-compose.yml"
    "docker-compose-kafka.yml"
    "docker-compose-statsd.yml"
    "docker-compose-telegraf.yml"
    "docker-compose-node-exporter.yml"
    "docker-compose-alloy.yml"
    "docker-compose-prometheus.yml"
    "docker-compose-loki.yml"
    "docker-compose-grafana.yml"
    "docker-compose-wrk.yml"
)

if [ "$1" == "dev" ]; then
    echo "Running in DEV mode with code mounts..."
    COMPOSE_FILES+=("docker-compose-app.dev.yml")
    shift # Удаляем 'dev' из аргументов
else
    echo "Running in PROD/STAGE mode (built image, no mounts)..."
    COMPOSE_FILES+=("docker-compose-app.yml")
fi

# Собираем строку через разделитель ':'
COMPOSE_FILE_STRING=$(IFS=:; echo "${COMPOSE_FILES[*]}")

export COMPOSE_PATH_SEPARATOR=:
export COMPOSE_FILE="$COMPOSE_FILE_STRING"

"$@"