"""
Тест метрик statsd client, api и ендпоинта /metrics
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


class TestStatsdMetricsLogic:
    """Тесты логики отправки метрик через middleware"""

    def test_statsd_metrics_are_sent_on_request(self):
        """
        Интеграционный тест логики отправки метрик.
        Проверяет, что при HTTP запросе middleware вызывает методы StatsD клиента
        c правильными именами метрик.

        Notes:
            Проверяем вызов incr (счетчик запросов)
            Проверяем вызов timing (гистограмма/таймер задержки)
            Проверяем, что значение задержки - число >= 0
        """
        from backend.app.main import app

        mock_statsd_client = MagicMock()

        with patch(
            "backend.app.middleware.logging.get_statsd_client",
            return_value=mock_statsd_client,
        ):
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200

            mock_statsd_client.incr.assert_called_once()
            incr_args = mock_statsd_client.incr.call_args[0][0]
            assert "http.requests" in incr_args
            assert "GET" in incr_args
            assert "200" in incr_args

            mock_statsd_client.timing.assert_called_once()
            timing_args = mock_statsd_client.timing.call_args[0][0]
            assert timing_args == "http.requests.duration"

            timing_value = mock_statsd_client.timing.call_args[0][1]
            assert isinstance(timing_value, (int, float))
            assert timing_value >= 0

    def test_statsd_client_creation_error_handling(self):
        """
        Проверяет, что если StatsD клиент не создался (вернул None),
        приложение не падает, a просто пропускает отправку метрик.
        """
        from backend.app.main import app

        with patch(
            "backend.app.middleware.logging.get_statsd_client", return_value=None
        ):
            client = TestClient(app)
            response = client.get("/health")
            assert response.status_code == 200


class TestMetricsEndpoint:
    """
    Тесты ендпоинта /metrics (Prometheus).
    """

    def test_metrics_endpoint_exists(self, client: TestClient):
        """
        Проверка доступности эндпоинта /metrics.
        Доступен только если DEBUG_MODE=True
        """
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_content_prometheus(self, client: TestClient):
        """
        Интеграционный тест: проверяет, что /metrics возвращает данные в формате Prometheus
        """
        response = client.get("/metrics")
        content = response.text

        assert (
            "http_requests_total" in content or "process_cpu_seconds_total" in content
        )

    def test_metrics_content_type(self, client: TestClient):
        """Проверка Content-Type ответа метрик."""
        response = client.get("/metrics")
        assert "text/plain" in response.headers["content-type"]


class TestApiEndpoints:
    """Тестирование основных API ендпоинтов"""

    def test_health_check(self, client: TestClient):
        """Тест ендпоинта здоровья"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_process_message_v1(self, client: TestClient):
        """Тест создания сообщения через v3 (db in memory)"""
        payload = {"data": "Test message v1"}
        response = client.post("/v3/process", json=payload)

        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert "text" in data
        assert data["text"] == "Test message v1"
        assert "created_at" in data

    def test_process_message_invalid(self, client: TestClient):
        """Тест валидации: пустой текст."""
        payload = {"data": ""}
        response = client.post("/v3/process", json=payload)

        assert response.status_code == 422

    def test_get_message_not_found(self, client: TestClient):
        """Тест получения несуществующего сообщения"""
        fake_id = "969dac05-3474-7da6-8000-be85ecf0a75c"
        response = client.get(f"/v3/message/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
