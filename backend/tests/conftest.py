"""
Настроки тестов
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """
    Устанавливает переменные окружения для тестов и очищает кэш настроек.
    """
    monkeypatch.setenv("DEBUG_MODE", "True")
    monkeypatch.setenv("GRANIAN_WORKERS", "1")
    monkeypatch.setenv("POSTGRES_USER", "test_admin")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("SECRET_KEY_FILE", "")
    monkeypatch.setenv("SESSION_MIDDLEWARE_SECRET_KEY_FILE", "")
    monkeypatch.setenv("POSTGRES_PASSWORD_FILE", "")


@pytest.fixture(scope="module")
def client():
    """
    Фикстура предоставляет TestClient.
    Мокает подключение к БД и Kafka, чтобы тесты работали без Docker.

    Notes:
        Создаем список патчей для lifespan (startup/shutdown)
    """
    from backend.app.main import app

    patches = [
        patch(
            "backend.app.db.asyncpg_pool.AsyncPGDatabase.connect",
            new_callable=AsyncMock,
        ),
        patch(
            "backend.app.db.asyncpg_pool.AsyncPGDatabase.disconnect",
            new_callable=AsyncMock,
        ),
        patch("backend.app.infra.kafka.kafka_producer.KafkaLogProducer.start"),
        patch("backend.app.infra.kafka.kafka_producer.KafkaLogProducer.stop"),
    ]

    for p in patches:
        p.start()

    with TestClient(app) as test_client:
        yield test_client

    for p in patches:
        p.stop()
