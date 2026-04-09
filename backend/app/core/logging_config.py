"""
Конфигурация структурированного логирования через structlog и Kafka.
"""

import logging

import structlog

from backend.app.core.config import settings
from backend.app.infra.kafka.kafka_producer import kafka_log_producer


class DropEvent(BaseException):
    """Исключение для прерывания цепочки обработки логов structlog."""

    pass


def kafka_sink_processor(_logger, _method_name, event_dict):
    """
    Процессор structlog. Отправляет данные в Kafka и обрывает цепочку.
    Ничего не возвращает в stdout, предотвращая дублирование логов.

    Args:
        _logger: Экземпляр логгера (не используется).
        _method_name: Имя метода логирования (не используется).
        event_dict: Словарь c данными события лога.

    Raises:
        structlog.DropEvent: Всегда выбрасывается для предотвращения вывода в stdout.

    Note:
        Если продюсер Kafka не готов, лог все равно удаляется, чтобы избежать
        TypeError в PrintLogger из-за неожиданных аргументов.
        ВАЖНО:
            Всегда выбрасываем DropEvent, чтобы structlog HE вызывал logger_factory.
            Это предотвращает TypeError: PrintLogger.msg() got an unexpected keyword argument 'workers'

    """
    if kafka_log_producer.is_running:
        log_entry = {
            "event": event_dict.get("event"),
            "level": event_dict.get("level"),
            "timestamp": event_dict.get("timestamp"),
            "request_id": event_dict.get("request_id"),
            "service": "abelo-app",
        }
        kafka_log_producer.send_log_sync(log_entry)

    raise structlog.DropEvent


def configure_logging() -> None:
    """
    Настраивает structlog для высоконагруженного прода.
    Использует:
        1. FilteringBoundLogger для мгновенной отсечки ненужных уровней (DEBUG/INFO в проде).
        2. orjson для сверхбыстрой сериализации в JSON.
        3. Кэширование логгеров для устранения оверхеда на создание.

    Returns:
        None: Функция настраивает глобальное состояние structlog и ничего не возвращает.

    Note:
        Конфигурация применяется глобально. После вызова этой функции менять настройки
        structlog нельзя без перезапуска процесса (в Docker контейнер перезапускается).
        Логи направляются исключительно в Kafka через kafka_sink_processor, вывод в stdout
        отключен выбросом DropEvent.

        - structlog.contextvars.merge_contextvars Добавляет контекстные переменные
          (например, request_id из middleware)
        - structlog.processors.add_log_level Добавляет уровень логирования в вывод
        - structlog.processors.format_exc_info Форматирует исключения (traceback) в поле 'exception'
        - structlog.processors.TimeStamper(fmt="iso", utc=True) Добавляет timestamp в формате ISO 8601 (UTC)
        - structlog.processors.JSONRenderer(serializer=orjson.dumps)
          Рендер в JSON c помощью orjson.dumps, возвращает bytes

        Важно:
        - cache_logger_on_first_use=True обеспечивает кэширование логгеров после первого использования.
        - wrapper_class=structlog.make_filtering_bound_logger(log_level) обеспечивает нулевую стоимость
          пропущенных логов (если уровень ниже установленного).
        - logger_factory=structlog.PrintLoggerFactory() Пишет байты напрямую в stdout
        - context_class=dict Стандартный класс логгера
    """

    log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO

    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            kafka_sink_processor,
            # structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        # logger_factory=structlog.BytesLoggerFactory(),
        logger_factory=structlog.PrintLoggerFactory(),
        context_class=dict,
    )


configure_logging()
logger = structlog.get_logger()
