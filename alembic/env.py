import asyncio
from logging.config import fileConfig
import os
import sys

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from alembic import context


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import Base và settings từ các file của bạn.
# Dựa trên cấu trúc thư mục, models.py nằm ở thư mục gốc.
from models import Base
from config import settings

# Lấy URL database từ settings của bạn
# Giả sử bạn có DATABASE_ASYNC_URL trong file config.py
# Nếu không, hãy sử dụng DATABASE_URL
SQLALCHEMY_DATABASE_URI = str(settings.DATABASE_URL)

# Đối tượng Alembic Config
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Đây là đối tượng MetaData của mô hình của bạn
# để hỗ trợ 'autogenerate'
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Chạy migration ở chế độ 'offline'."""
    url = SQLALCHEMY_DATABASE_URI
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Cấu hình và chạy migration."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Chạy migration ở chế độ 'online'."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = SQLALCHEMY_DATABASE_URI
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
