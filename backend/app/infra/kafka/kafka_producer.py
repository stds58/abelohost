"""
Kafka Producer для отправки логов.
"""

import orjson
from confluent_kafka import Producer

from backend.app.core.config import settings


class KafkaLogProducer:
    """
    Продюсер Kafka для асинхронной отправки логов.
    Использует librdkafka для фоновой отправки сообщений.
    """

    def __init__(self):
        self._producer: Producer | None = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """
        Публичное свойство для проверки состояния продюсера.

        Returns:
            bool: True, если продюсер запущен и готов к отправке.
        """
        return self._is_running

    def start(self) -> None:
        """
        Инициализирует продюсера.
        Вызывается синхронно при старте приложения.

        Notes:
            - linger.ms: Ждем немного, чтобы набрать батч. Для логов 5-10ms идеально
            - batch.num.messages: Макс сообщений в батче.
            - queue.buffering.max.messages: Размер внутренней очереди librdkafka.
              Если приложение генерирует логи быстрее, чем сеть отправляет,
              они копятся здесь. 50к сообщений ~ несколько сотен МБ.
        """
        if self._is_running:
            return

        bootstrap_servers = getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

        conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "abelo-app-logger",
            "acks": 1,
            "linger.ms": 5,
            "batch.num.messages": 10000,
            "queue.buffering.max.messages": 50000,
        }

        self._producer = Producer(conf)
        self._is_running = True
        print("[Kafka] Confluent Producer initialized (native thread)")

    def stop(self) -> None:
        """
        Останавливает продюсер, дожидаясь отправки остатков очереди.

        Notes:
            self._producer.flush(timeout=5) Ждем до 5 секунд, пока очередь не опустеет
        """
        if not self._is_running:
            return

        print("[Kafka] Flushing remaining logs...")
        self._producer.flush(timeout=5)
        self._is_running = False
        print("[Kafka] Producer stopped")

    def send_log_sync(self, log_entry: dict) -> None:
        """Отправляет лог в Kafka.

        Librdkafka сам управляет очередью и сетью в фоновом потоке.

        Args:
            log_entry: Словарь c данными лога для сериализации.

        Note:
            - Если внутренняя очередь переполнена (BufferError), лог silently удаляется,
              чтобы не блокировать основное приложение.
            - self._producer.poll(0) poll(0) необходим для обработки коллбеков доставки (delivery reports).
              Без этого память под отправленные сообщения может не освобождаться.
        """
        if not self._is_running or not self._producer:
            return

        try:
            self._producer.poll(0)

            self._producer.produce(
                topic="app-logs",
                value=orjson.dumps(log_entry),
                on_delivery=self._delivery_report,
            )
        except BufferError:
            pass
        except Exception as e:
            print(f"[Kafka] Critical produce error: {e}")

    def _delivery_report(self, err, _msg) -> None:
        """Коллбек, вызываемый librdkafka при доставке (или ошибке) сообщения.

        Выполняется в фоновом потоке.

        Args:
            err: Ошибка доставки, если она произошла.
            _msg: Сообщение, которое было отправлено.
        """
        if err is not None:
            pass


kafka_log_producer = KafkaLogProducer()
