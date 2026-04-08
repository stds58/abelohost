import orjson
from confluent_kafka import Producer

from backend.app.core.config import settings


class KafkaLogProducer:
    def __init__(self):
        self._producer: Producer | None = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """Публичное свойство для проверки состояния продюсера."""
        return self._is_running

    def start(self) -> None:
        """
        Инициализирует продюсер.
        Вызывается синхронно при старте приложения.
        """
        if self._is_running:
            return

        bootstrap_servers = getattr(settings, "KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

        conf = {
            "bootstrap.servers": bootstrap_servers,
            "client.id": "abelo-app-logger",
            "acks": 1,
            # linger.ms: Ждем немного, чтобы набрать батч.
            # Для логов 5-10ms идеально.
            "linger.ms": 5,
            # batch.num.messages: Макс сообщений в батче.
            "batch.num.messages": 10000,
            # queue.buffering.max.messages: Размер внутренней очереди librdkafka.
            # Если приложение генерирует логи быстрее, чем сеть отправляет,
            # они копятся здесь. 50к сообщений ~ несколько сотен МБ.
            "queue.buffering.max.messages": 50000,
        }

        self._producer = Producer(conf)
        self._is_running = True
        print("[Kafka] Confluent Producer initialized (native thread)")

    def stop(self) -> None:
        """
        Останавливает продюсер, дожидаясь отправки остатков очереди.
        """
        if not self._is_running:
            return

        print("[Kafka] Flushing remaining logs...")
        # Ждем до 5 секунд, пока очередь опустеет
        self._producer.flush(timeout=5)
        self._is_running = False
        print("[Kafka] Producer stopped")

    def send_log_sync(self, log_entry: dict) -> None:
        """
        Отправляет лог в Kafka.
        Librdkafka сам управляет очередью и сетью в фоновом потоке.
        """
        if not self._is_running or not self._producer:
            return

        try:
            # poll(0) необходим для обработки коллбеков доставки (delivery reports).
            # Без этого память под отправленные сообщения может не освобождаться.
            self._producer.poll(0)

            self._producer.produce(
                topic="app-logs",
                value=orjson.dumps(log_entry),
                # on_delivery вызывается из фонового потока librdkafka после подтверждения брокером
                on_delivery=self._delivery_report,
            )
        except BufferError:
            # Внутренняя очередь librdkafka переполнена.
            # Дропаем лог, чтобы не вешать приложение.
            pass
        except Exception as e:
            print(f"[Kafka] Critical produce error: {e}")

    def _delivery_report(self, err, _msg) -> None:
        """
        Коллбек, вызываемый librdkafka при доставке (или ошибке) сообщения.
        Выполняется в фоновом потоке.
        """
        if err is not None:
            # Можно залогировать ошибку, но осторожно, чтобы не создать рекурсию,
            # если логгер тоже пытается отправить в Kafka.
            # print(f'[Kafka] Message delivery failed: {err}')
            pass


kafka_log_producer = KafkaLogProducer()
