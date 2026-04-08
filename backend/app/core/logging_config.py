import logging

import structlog

from backend.app.core.config import settings
from backend.app.infra.kafka.kafka_producer import kafka_log_producer


class DropEvent(BaseException):
    pass


def kafka_sink_processor(_logger, _method_name, event_dict):
    """
    Процессор structlog. Отправляет данные в Kafka и ОБРЫВАЕТ цепочку.
    Ничего не возвращает в stdout.
    """
    # Если продюсер не готов, мы все равно должны дропнуть лог,
    # чтобы не упала ошибка в PrintLogger из-за kwargs.
    if kafka_log_producer.is_running:
        log_entry = {
            "event": event_dict.get("event"),
            "level": event_dict.get("level"),
            "timestamp": event_dict.get("timestamp"),
            "request_id": event_dict.get("request_id"),
            "service": "abelo-app",
        }
        kafka_log_producer.send_log_sync(log_entry)

    # ВАЖНО: Всегда выбрасываем DropEvent, чтобы structlog HE вызывал logger_factory.
    # Это предотвращает TypeError: PrintLogger.msg() got an unexpected keyword argument 'workers'
    raise structlog.DropEvent


def configure_logging() -> None:
    """
    Настраивает structlog для высоконагруженного продакшена.

    Использует:
    1. FilteringBoundLogger для мгновенной отсечки ненужных уровней (DEBUG/INFO в проде).
    2. orjson для сверхбыстрой сериализации в JSON.
    3. BytesLoggerFactory для записи байтов напрямую в stdout (минуя кодировку str).
    4. Кэширование логгеров для устранения оверхеда на создание.
    """

    # Определяем уровень логирования из настроек
    log_level = logging.DEBUG if settings.DEBUG_MODE else logging.INFO

    structlog.configure(
        # 1. Кэширование: создает логгер один раз, далее использует ссылку.
        # Важно: после вызова configure() менять настройки нельзя (но в Docker контейнер перезапускается).
        cache_logger_on_first_use=True,
        # 2. Wrapper Class: Самый быстрый способ фильтрации.
        # Если уровень ниже log_level, метод просто возвращает None.
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        processors=[
            # Добавляет контекстные переменные (например, request_id из middleware)
            structlog.contextvars.merge_contextvars,
            # Добавляет уровень логирования в вывод
            structlog.processors.add_log_level,
            # Форматирует исключения (traceback) в поле 'exception'
            structlog.processors.format_exc_info,
            # Добавляет timestamp в формате ISO 8601 (UTC)
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            kafka_sink_processor,
            # 3. Рендеринг в JSON c помощью orjson
            # orjson.dumps возвращает bytes, что идеально для BytesLoggerFactory
            # structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        # 4. Factory: Пишет байты напрямую в stdout.
        # Это быстрее, чем TextIOWrapper, так как avoids extra encoding steps.
        # logger_factory=structlog.BytesLoggerFactory(),
        logger_factory=structlog.PrintLoggerFactory(),
        # Стандартный класс логгера (не используется при wrapper_class выше, но good to have)
        context_class=dict,
    )


# Вызываем конфигурацию сразу при импорте модуля,
# либо можно вызывать явно в main.py перед созданием app.
# Для надежности лучше вызывать явно в lifespan, но для structlog часто достаточно раннего импорта.
configure_logging()

# Экспортируем готовый к использованию логгер для удобства импорта в других модулях
logger = structlog.get_logger()
