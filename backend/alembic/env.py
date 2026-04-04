import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы можно было импортировать 'backend'
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
import importlib
from logging.config import fileConfig

from backend.app.core.config import settings
from backend.app.db.base import Base
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context


def import_all_models(root_path: Path, base_package: str):
    """Импортирует все файлы models.py, найденные рекурсивно."""
    for model_file in root_path.rglob("models.py"):
        # Пропускаем __pycache__, тесты и т.п., если нужно
        if "test" in str(model_file) or "__pycache__" in str(model_file):
            continue

        # Преобразуем путь в имя модуля
        rel_path = model_file.relative_to(root_path)
        module_name = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
        full_module_name = f"{base_package}.{module_name}"

        print(f"Importing: {full_module_name}")
        try:
            importlib.import_module(full_module_name)
        except Exception as e:
            print(f"Failed to import {full_module_name}: {e}")


# Импортируем все models.py рекурсивно
BACKEND_DIR = PROJECT_ROOT / "backend"
import_all_models(BACKEND_DIR / "app", "backend.app")


# alembic revision --autogenerate -m "Auto-generated migration"
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
sqlalchemy_url = settings.DATABASE_URL
config.set_main_option("sqlalchemy.url", sqlalchemy_url)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# def do_run_migrations(connection: Connection) -> None:
#     context.configure(connection=connection, target_metadata=target_metadata)
#
#     with context.begin_transaction():
#         context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # ← включает сравнение длины VARCHAR и т.п.
        compare_server_default=True,  # ← опционально, для server_default
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
