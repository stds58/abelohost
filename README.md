# Abelo PLG Fastapi orm benchmark

**Требования**

- Python 3.10+.
- FastAPI для API.
- SQLAlchemy с PostgreSQL (для простоты, храните mock-данные или логи, если нужно).
- Prometheus для сбора метрик
- Node Exporter для системных метрик (CPU, memory в контейнере).
- Grafana для дашбордов (provisioning с JSON-файлами).
- Structured logging (JSON с logging или structlog).
- Docker и Docker Compose.
- Pytest для тестов.
- Читаемый код с type hints, docstrings, обработкой ошибок и базовой безопасностью (OWASP: валидация input).

**Задача**

- FastAPI-приложение:

      Создайте простое приложение со следующими эндпоинтами:
          GET /health: Возвращает {"status": "healthy"}.
          GET /message/{id}: Возвращает статическое сообщение (например, из mock-БД в PostgreSQL: таблица messages с id, text).
          POST /process: Принимает JSON ({"data": str}), симулирует обработку (sleep ~0.5s для latency) и возвращает echo.
          GET /metrics: Экспорт Prometheus-метрик (автоматически через instrumentator).
      Добавьте кастомные метрики: 
          Счетчик запросов по эндпоинтам (Counter), гистограмма latency (Histogram).
      Логи:  
          Структурированные JSON-логи.

- Observability:

      Интегрируйте Prometheus:  
          Собирайте метрики приложения (requests total, latency, errors) 
          и системные от Node Exporter (CPU, mem, disk).
      Логи:  
          Настройте сбор логов (Alloy/Promtail) и отправку их в Loki.
      Grafana:  
          Создайте дашборд (JSON-export в репо) с панелями: 
          Графики запросов/sec, latency percentile, CPU/mem usage, 
          логи приложения, counter для errors/warnings.

- Заполнение данными:

      Mock-данные в PostgreSQL: ≥10 сообщений (seed-скрипт при старте).
- Оптимизация и анализ:

      Симулируйте bottleneck (медленный запрос), опишите в README, как выявить (через Grafana queries).
      Добавьте алерт-rule в Prometheus (например, high latency >1s).

- Контейнеризация:

      Безопасный Dockerfile для приложения.
      Docker Compose со всеми необходимыми сервисами.

- Тестирование:

        Pytest: Unit для эндпоинтов, интеграционные для метрик (проверьте /metrics response).

**Документация**

- Напишите README.md:

      Инструкция по запуску приложения локально через Docker Compose
      Объяснение метрик/логов

- Добавьте файл JSON-export из созданной вами дашбордой в репозиторий

     GitHub

- Код должен быть выложен на GitHub. Проекты с одним коммитом рассматриваться не будут.
 

## О проекте

```text
высоконагруженное приложение на **FastAPI + Granian**, 
предназначенное для сравнительного анализа 
производительности различных слоев доступа к данным в асинхронной среде Python

Проект демонстрирует построение наблюдаемого (Observable) сервиса,
сравнительный анализ (RPS, Latency) в FastAPI 
в зависимости от инструмента доступа к данным (SqlAlchemy, Async_pg, db in memory)
с акцентом на точный сбор метрик в многопроцессной архитектуре (Granian Workers) 
через **StatsD** вместо стандартных Prometheus-инструментаторов.
```

## Ключевые особенности

### 1. Сравнительный анализ Data Access Layers
Приложение реализует единый интерфейс репозитория (`MessageRepository`) с четырьмя различными реализациями для сравнения скорости чтения/записи (RPS, Latency):
*   **In-Memory:** Словарь Python (эталон скорости, без I/O).
*   **Asyncpg:** Прямой драйвер PostgreSQL (минимальные накладные расходы, ручное управление SQL).
*   **SQLAlchemy ORM:** Асинхронный ORM (удобство разработки vs оверхед маппинга).
*   **Dummy/Mock:** Возврат статических словарей (оценка накладных расходов самого фреймворка FastAPI/Granian).

### 2. Архитектура Observability (StatsD + Granian)
Вместо стандартного `prometheus-fastapi-instrumentator` используется связка **StatsD Client + StatsD Exporter**.
*   **Почему?** Granian запускает приложение в нескольких процессах (workers). Стандартные инструменты часто агрегируют метрики неточно или создают блокировки GIL.
*   **Решение:** Каждый воркер отправляет метрики с префиксом `worker_<PID>`, что позволяет видеть нагрузку на каждый процесс отдельно в Grafana.

### 3. Полный стек мониторинга (PLG + Telegraf)
*   **Logs:** Структурированные JSON-логи через `structlog` → Kafka → Grafana Alloy → Loki.
*   **Metrics:** App Metrics (StatsD) + System Metrics (Node Exporter/Telegraf) → Prometheus → Grafana.
*   **Tracing:** Внедрение `request_id` (UUIDv7) в каждый лог и ответ API для сквозной отладки запросов.


## Архитектура проекта

### Используемые технологии

![Python 3.13](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Structlog](https://img.shields.io/badge/Structlog-555555?style=for-the-badge&logo=python&logoColor=white)
![orjson](https://img.shields.io/badge/orjson-555555?style=for-the-badge&logo=rust&logoColor=white)
![Granian](https://img.shields.io/badge/Granian-555555?style=for-the-badge&logo=rust&logoColor=white)<br>
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Alembic](https://img.shields.io/badge/Alembic-555555?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![asyncpg](https://img.shields.io/badge/asyncpg-555555?style=for-the-badge&logo=postgresql&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-231F20?style=for-the-badge&logo=apache-kafka&logoColor=white)<br>
![StatsD](https://img.shields.io/badge/StatsD-555555?style=for-the-badge&logo=datadog&logoColor=white)
![Node Exporter](https://img.shields.io/badge/Node_Exporter-555555?style=for-the-badge&logo=linux&logoColor=white)
![Telegraf](https://img.shields.io/badge/Telegraf-22A699?style=for-the-badge&logo=influxdb&logoColor=white)
![Grafana Alloy](https://img.shields.io/badge/Grafana_Alloy-555555?style=for-the-badge&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Loki](https://img.shields.io/badge/Loki-FFD142?style=for-the-badge&logo=grafana&logoColor=black)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)<br>
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![uv](https://img.shields.io/badge/uv-555555?style=for-the-badge&logo=python&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-555555?style=for-the-badge&logo=python&logoColor=white)
![Black](https://img.shields.io/badge/Black-555555?style=for-the-badge&logo=github&logoColor=white)
![Pylint](https://img.shields.io/badge/Pylint-555555?style=for-the-badge&logo=python&logoColor=white)
![Pre-commit](https://img.shields.io/badge/Pre--commit-555555?style=for-the-badge&logo=git&logoColor=white)


### Ключевые архитектурные решения:

**Разделение сбора метрик**
```text
Разделение сбора метрик
│
├─ App Metrics (Business Logic)
│    │
│    ├── APP -> STATS-D (UDP) -> STATS-D EXPORTER -> PROMETHEUS
│    │       эффективный подход при многоворкерности Granian
│    │       Почему: Stats-d умеет собирать метрики с каждого воркера
│    │
│    └── APP -> PROMETHEUS-FASTAPI-INSTRUMENTATOR -> /metrics endpoint -> PROMETHEUS
│            неэффективный подход
│            Почему: prometheus-fastapi-instrumentator не умеет 
│            автоматически объединять метрики со всех воркеров в один ответ на /metrics
│
├─ Infra Metrics (Containers):**
│    │
│    └── DOCKER SOCKET -> TELEGRAF -> PROMETHEUS
│            Почему: Telegraf лучше интегрируется с Docker API 
│            для получения точных данных по изоляции ресурсов контейнеров
│        
└─ Host Metrics (OS):**
     │
     └── NODE EXPORTER -> PROMETHEUS
             Почему: Стандарт де-факто для мониторинга железа
```
**Поток логов (Log Pipeline)**
```text
Поток логов (Log Pipeline)
     │
     └── APP -> STRUCTLOG -> KAFKA -> ALLOY -> LOKI -> GRAFANA
             Использование Kafka здесь оправдано высокой нагрузкой: 
             если Loki временно недоступен или тормозит, логи не теряются, а накапливаются в Kafka
```
**Безопасность**
```text
Безопасность
│
├─ Файловая система
│    ├── Там, где возможно, сервисы запущены с файловой системой только для чтения "read_only: true"
│    ├── Небольшие данные пишутся в память "tmpfs: /tmp:size=64m,mode=1777"
│    └── Большие данные, которые нельзя терять, пишутся в тома
│
├─ Привилегии процесса на уровне ядра (drop all capabilities)
│    └── Во всех сервисах отозваны все capabilities "cap_drop: ALL", 
│        даны только необходимые capabilities, если сервису они нужны для работы
│        CHOWN           Смена владельца файлов
│        FOWNER          Игнорирование проверки владельца при установке прав
│        DAC_OVERRIDE    Игнорирование ограничений прав доступа (критично для initdb на ro fs)
│        SETUID          Переключение пользователя
│        SETGID          Переключение группы
│        KILL            Для корректного завершения процессо   
│
├─ Профиль безопасности Seccomp
│    └── используется профиль докера по умолчанию
│
├─ Сетевая изоляция
│    └── частичная. все контейнеры в одной сети, но для отладки порты проброшены наружу
│        открытые порты:
│        app 8000
│        grafana 3000
│        prometheus 9090
│        alloy 12345
│
├─ Секреты
│    └── пароли и ключи передаются через Docker Secrets, а не через переменные окружения
│
├─ Distroless образы (без командных оболочек bash, shell и тд)
│    └── нет
│
├─ Непривилегированный пользователь
│    └── образ для FastAPI запущен от UID=1000
│        остальные образы - зависит от разработчика образа
│
├─ Сканирование образов на уязвимости
│    └── нет
│
├─ Ораничение ресурсов (защита от DOS шумных соседей)
│    └── 
│
├─ Usernamespaces (даже если в контейнере процесс работает от root, на хост он будет мапиться как непривилигерованный пользователь)
│    └── нет
│
├─ Подписывание образов и проверка подписи при запуске
│    └── нет
│
├─ Запрет процессу получить новые привилегии
│    └── Все сервисы запущены с "security_opt: no-new-privileges:true"
│
└─ .dockerignore
     └── есть          
```

### Топология

**хост WSL**
- DOCKER SOCKET (/var/run/docker.sock) Unix-сокет, который является точкой входа для Docker API

**abelo-app**
- APP (FastAPI бекенд)
- STATS-D (UDP) легкий, быстрый и тупой посредник, который позволяет воркерам Granian сбрасывать метрики асинхронно и без блокировок
- STRUCTLOG (Структурированное логирование)
- PROMETHEUS-FASTAPI-INSTRUMENTATOR (Библиотека, которая автоматически добавляет стандартные метрики Prometheus в приложение на FastAPI)

**abelo-db** 
- POSTGRES (База данных)

**abelo-alloy** 
- ALLOY (Агент сбора и процессинга логов) Забирает логи из Kafka, парсит JSON-структуру, обогащает метаданными (labels) и отправляет в Loki

**abelo-grafana** 
- GRAFANA (Визуализация) платформа для визуализации, анализа и мониторинга метрик, логов и трассировок

**abelo-kafka** 
- KAFKA (Брокер сообщений, буферизация данных и ослабление связей между сервисами) Транспорт для логов. Гарантирует сохранность данных при пиковых нагрузках и отвязывает приложение от скорости работы системы логирования

**abelo-loki** 
- LOKI (Хранилище логов) горизонтально масштабируемая, высокодоступная и многопользовательская система агрегации логов

**abelo-node-exporter** 
- NODE EXPORTER (Системные метрики)

**abelo-prometheus** 
- PROMETHEUS (Сбор метрик, алертинг)

**abelo-statsd-exporter** 
- STATS-D EXPORTER (Транслятор метрик. Превращает UDP пакеты StatsD в метрики Prometheus)

**abelo-telegraf** 
- TELEGRAF (Агент для сбора и отправки метрик Docker контейнеров)

**load-test** 
- WRK (нагрузочное тестирование) Запускается по профилю `load-test`. Использует Lua-скрипт `post.lua` для POST запросов.


<details>
  <summary><strong>СТРУКТУРА ПРОЕКТА</strong></summary>

```text
abelohost/
├── backend
│   ├── alembic
│   │   ├── versions
│   │   │   └── f938e77056d0_auto_generated_migration.py
│   │   ├── env.py
│   │   └── README
│   ├── app
│   │   ├── api
│   │   │   ├── v1
│   │   │   │   ├── endpoints
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── schemas
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── deps.py
│   │   │   │   └── router.py
│   │   │   ├── v2
│   │   │   │   ├── endpoints
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── schemas
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── deps.py
│   │   │   │   └── router.py
│   │   │   ├── v3
│   │   │   │   ├── endpoints
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── schemas
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message.py
│   │   │   │   ├── __init__.py
│   │   │   │   ├── deps.py
│   │   │   │   └── router.py
│   │   │   └── __init__.py
│   │   ├── application
│   │   │   ├── repositories
│   │   │   │   ├── __init__.py
│   │   │   │   └── message.py
│   │   │   ├── use_cases
│   │   │   │   ├── __init__.py
│   │   │   │   ├── create_message.py
│   │   │   │   └── get_message.py
│   │   │   └── __init__.py
│   │   ├── core
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   └── logging_config.py
│   │   ├── db
│   │   │   ├── __init__.py
│   │   │   ├── annotations.py
│   │   │   ├── asyncpg_pool.py
│   │   │   ├── base.py
│   │   │   ├── deps.py
│   │   │   └── session.py
│   │   ├── domain
│   │   │   ├── entities
│   │   │   │   ├── __init__.py
│   │   │   │   └── message.py
│   │   │   ├── exceptions
│   │   │   │   ├── __init__.py
│   │   │   │   └── message.py
│   │   │   ├── tests
│   │   │   │   ├── __init__.py
│   │   │   │   └── test_message_domain.py
│   │   │   ├── value_objects
│   │   │   │   ├── __init__.py
│   │   │   │   └── message.py
│   │   │   └── __init__.py
│   │   ├── exceptions
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── database.py
│   │   │   ├── handlers.py
│   │   │   └── http_exceptions.py
│   │   ├── infra
│   │   │   ├── adapters
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asyncpg_message_repository.py
│   │   │   │   ├── in_memory_message_repository.py
│   │   │   │   └── sql_alchemy_message_repository.py
│   │   │   ├── db
│   │   │   │   ├── __init__.py
│   │   │   │   └── models.py
│   │   │   ├── kafka
│   │   │   │   ├── __init__.py
│   │   │   │   └── kafka_producer.py
│   │   │   └── __init__.py
│   │   ├── middleware
│   │   │   ├── __init__.py
│   │   │   └── logging.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── __init__.py
│   ├── alembic.ini
│   ├── Dockerfile
│   └── entrypoint.sh
├── observability
│   ├── alloy
│   │   └── config.alloy
│   ├── grafana
│   │   ├── dashboards
│   │   │   └── abelo-dashboard-statsd.json
│   │   └── provisioning
│   │       ├── dashboards
│   │       │   └── dashboards.yml
│   │       └── datasources
│   │           └── datasources.yml
│   ├── loki
│   │   └── local-config.yaml
│   ├── prometheus
│   │   ├── rules
│   │   │   └── alerts.yml
│   │   └── prometheus.yml
│   ├── statsd
│   │   └── mapping.yaml
│   └── telegraf
│       └── telegraf.conf
├── postgres_config
│   └── postgresql.conf
├── scripts
│   ├── apply_migration.py
│   └── make_new_migration.py
├── secrets
│   ├── db_password.txt
│   ├── grafana_admin_password.txt
│   ├── grafana_admin_user.txt
│   ├── secret_key.txt
│   └── session_middleware_secret_key.txt
├── wrk_lua
│   └── post.lua
├── .dockerignore
├── .env
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── docker-compose-alloy.yml
├── docker-compose-app.dev.yml
├── docker-compose-app.yml
├── docker-compose-grafana.yml
├── docker-compose-kafka.yml
├── docker-compose-loki.yml
├── docker-compose-node-exporter.yml
├── docker-compose-prometheus.yml
├── docker-compose-statsd.yml
├── docker-compose-telegraf.yml
├── docker-compose-wrk.yml
├── docker-compose.yml
├── pyproject.toml
├── README.md
└── start.sh
```

</details>


## Первый запуск

**1 Клонируем проект**

    git clone https://github.com/stds58/abelohost.git

**2 Создаём виртуальное окружение. Нужно для удобства отображения импортов в IDE, весь код у нас работает в докере**

в docker-compose-app.dev.yml как volume прокинута папка /backend, поэтому любые изменения в файлах, которые делаются в IDE локально, 
видны в докере, благодаря чему граниан автоматически перезапускается.

windows
```text
python -m venv venv
```
```text
.venv\scripts\activate
```
linux, mac
```text
python3 -m venv .venv
```
```text
source .venv/bin/activate
```
**3 Устанавливаем зависимости**

Установка пакетного менеджера uv: 
```text
pip install uv
```

Установка зависимостей:
```text
uv sync --group main --group linter --group test
```

```text
⚠️ 
группы:
main....основные зависимости, которые будут и на проде
linter..линтеры и форматеры кода
test....пакеты для тестирования

Все пакеты устанавливаются в virtual env, расположенный в .venv
```

установка хуков для пре коммитов
```text
pre-commit install -t pre-commit -t pre-push
```

создание .env в корне проекта
```text
POSTGRES_USER=admin
POSTGRES_DB=abelo_db
GRANIAN_WORKERS=6
```

**4 telegraf**

в группу docker на хост-машине добавить пользователя, от имени которого Telegraf работает внутри контейнера
```text
wsl getent group docker
```
пример ответа:

    wsl docker:x:1001:your_user_name

UID пользователя добавить в файл docker-compose-telegraf.yml

```yaml
    group_add:
      - "1001"
```

**5 Разворачиваем в докере**

запустить фастапи в режиме DEBUG_MODE=True
1 воркер granin, reload
```text
wsl ./start.sh dev docker compose up --build
```

запустить фастапи в режиме DEBUG_MODE=False
```text
wsl ./start.sh docker compose up --build
```

**6 Миграции в пустую бд**

dev
```text
если ещё не проинизиализирован алембик, но в проекте он проинициализирован
uv run alembic init backend/alembic
```
```text
python scripts/apply_migration.py
```

не dev:
миграции применятся автоматически

**Залить данные в бд**


**8 Проверка безопасности сервисов**

1. Проверка того, что контейнер работает от non-root
```text
docker exec abelo-app id
Ожидается: uid=1000(appuser) gid=1000(appuser)
```
2. Проверка read-only ФС
```text
docker exec abelo-app touch /etc/test 2>&1
Ожидается: Read-only file system
```
3. Проверка секретов
```text
docker exec abelo-app cat /run/secrets/db_password
Ожидается: ваш пароль
```
4. Проверка лимитов
```text
docker stats abelo-app
Смотрите колонки CPU%, MEM USAGE
```
5. Проверка seccomp (расширенный режим)
```text
docker inspect abelo-app --format='{{.HostConfig.SecurityOpt}}'
```
6. Проверка capabilities (drop ALL)
```text
docker exec abelo-app bash -c "cat /proc/1/status | grep Cap"

Чтобы убедиться, что процесс не сможет получить новые привилегии даже через setuid бинарники
docker exec abelo-app bash -c "cat /proc/1/status | grep NoNewPrivs"

docker exec -it abelo-app bash
Попытка записать в системную папку touch /etc/test_file
Попытка установить программу apt-get update
Попытка стать root через sudo (если вдруг установлено) sudo ls
Проверка, кто ты есть whoami
Проверка, кто ты есть id

интерактивный вход
По SSH
ssh appuser@server
$  # ← ты получил интерактивную оболочку

В Dockerе
docker exec -it abelo-app bash
$  # ← ты получил интерактивную оболочку

шелл пользователя
docker exec abelo-app getent passwd appuser
Попробуй войти под ним (внутри контейнера)
docker exec abelo-app bash -c "su - appuser"
Результат: su сессия сразу закроется
```

**8 Проверка доступности сервисов, сваггер, графики**

[сваггер](http://0.0.0.0:8000/api/docs)<br>
[grafana](http://localhost:3000/d/abelo-monitoring-statsd/)<br>
[prometheus: поставщики метрик](http://0.0.0.0:9090/targets?search=)<br>
[prometheus: алерты](http://0.0.0.0:9090/alerts?search=)<br>
[Fastapi health](http://0.0.0.0:8000/health)<br>
[Fastapi проверка связи с бд через sqlalchemy](http://0.0.0.0:8000/check_sqlalchemy_db-info)<br>
[Fastapi проверка связи с бд через asyncpg](http://0.0.0.0:8000/check_asyncpg_db-info)<br>
[alloy](http://localhost:12345/graph)

**Нагрузочное тестирование**

wsl ./start.sh docker compose --profile load-test up load-test

**9 Данные в бд**

wsl ./start.sh exec abelo-db psql -U admin -d abelo_db
docker-compose exec abelo-db psql -U admin -d abelo_db
SELECT COUNT(1) as cnt FROM messages;



**9 Удаление/остановка контейнеров**

удалить все контейнеры, но оставить данные в БД (данные останутся только в dev)

    wsl ./start.sh docker compose down

удалить все контейнеры и данные в БД

    wsl ./start.sh docker compose down -v


## Разработка

**Запуск линтеров перед коммитом**

Форматирование
```text
uv run black .
```
Линтинг + автоисправление
```text
uv run ruff check . --fix
```
Глубокая проверка (Pylint)
```text
uv run pylint backend/
```
Поиск мёртвого кода
```text
uv run vulture backend/ vulture-whitelist.py
```

**Тесты**

запустить тесты для модуля identity (подставить свой модуль)

    pytest backend/ -v
    pytest backend/tests/

запустить тесты для файла test_identity_api.py с выводом принтов из теста

    uv run pytest backend/app/domain/tests/test_message_domain.py -v
    uv run pytest backend/app/domain/tests/test_message_domain.py::TestMessageDomain::test_message_immutability -v -s


## Мониториг


**Логи**

посмотреть логи контейнера с фастапи

    docker logs -f preview-fastapi-app







