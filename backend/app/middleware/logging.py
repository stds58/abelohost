r"""
Middleware для внедрения request_id и отправки метрик в StatsD.

Полное имя метрики c префиксом будет:
abelo_app.worker_<PID>.http.requests.<METHOD>.<STATUS>
Разберем по частям для regex abelo_app.worker_*\.http.requests.*.*:

    abelo_app.worker_ — фиксированная часть.
    * (первая звезда) — захватывает PID. Это $1.
    \.http.requests. — фиксированная часть.
    * (вторая звезда) — захватывает METHOD. Это $2.
    . — разделитель.
    * (третья звезда) — захватывает STATUS. Это $3.

"""

import os
import time

import statsd
import structlog
from fastapi import Request, Response
from uuid_extensions import uuid7

from backend.app.core.logging_config import logger as structlog_logger

STATSD_HOST = "statsd-exporter"
STATSD_PORT = 8125

_statsd_client = None


def get_statsd_client():
    """Ленивая инициализация клиента StatsD.

    Создает клиент c префиксом, содержащим PID воркера, для разделения метрик
    в многопроцессной среде.

    Returns:
        statsd.StatsClient | None: Клиент StatsD или None при ошибке инициализации.
    """
    global _statsd_client
    if _statsd_client is None:
        pid = os.getpid()
        prefix = f"abelo_app.worker_{pid}"
        try:
            _statsd_client = statsd.StatsClient(
                host=STATSD_HOST, port=STATSD_PORT, prefix=prefix
            )
        except Exception as e:
            structlog_logger.error("statsd_init_failed", error=str(e))
            return None
    return _statsd_client


async def structlog_middleware(request: Request, call_next):
    """Middleware для внедрения request_id (UUID7) в контекст логов и отправки метрик в StatsD.

    Args:
        request: Входящий HTTP запрос FastAPI.
        call_next: Следующий обработчик в цепочке middleware.

    Returns:
        Response: HTTP ответ от приложения.
    """
    request_id = str(uuid7())

    start_time = time.time()

    with structlog.contextvars.bound_contextvars(request_id=request_id):
        response: Response = await call_next(request)

        process_time = (time.time() - start_time) * 1000

        client = get_statsd_client()

        if client:
            try:
                client.incr(f"http.requests.{request.method}.{response.status_code}")
                client.timing("http.requests.duration", process_time)
            except Exception as e:
                structlog_logger.warning("statsd_send_failed", error=str(e))

        response.headers["X-Request-ID"] = request_id
        return response
