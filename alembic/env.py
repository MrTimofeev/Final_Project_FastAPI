# alembic/env.py
from __future__ import with_statement
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from logging import getLogger
from alembic import context

import os
import sys
from dotenv import load_dotenv

# Подгружаем .env
load_dotenv()

# Добавляем корень проекта в путь
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.models import *  # Это должно загрузить все модели
from app.database.database import Base

# Конфигурация Alembic
config = context.config

# Настройка логов
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ✅ Указываем метаданные ПОСЛЕ импорта моделей
target_metadata = Base.metadata

# Получаем DATABASE_URL из .env
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в переменных окружения")

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())