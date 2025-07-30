import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config # Được giữ lại theo template Alembic, không dùng trực tiếp
from sqlalchemy import pool # Được giữ lại theo template Alembic, không dùng trực tiếp
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# Đây là đối tượng Alembic Config, cung cấp
# quyền truy cập vào các giá trị trong file .ini đang được sử dụng.
config = context.config

# Giải thích file cấu hình cho logging của Python.
# Dòng này thiết lập các logger cơ bản.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MỚI: Thêm đường dẫn dự án vào sys.path để có thể import các module từ thư mục gốc
import sys
from pathlib import Path

# Giả định env.py nằm trong thư mục_gốc_dự_án/alembic/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# MỚI: Import Base từ models.py (nơi bạn định nghĩa các mô hình SQLAlchemy)
# Đảm bảo models.py của bạn có dòng: Base = declarative_base()
# THAY docker_Todos BẰNG TÊN THƯ MỤC GỐC DỰ ÁN CỦA BẠN NẾU KHÁC!
from models import Base

# MỚI: Import settings từ config.py (để lấy DATABASE_URL)
from config import settings

# Đây là đối tượng MetaData của mô hình của bạn
# để hỗ trợ 'autogenerate'
target_metadata = Base.metadata


# Các giá trị khác từ cấu hình, được định nghĩa bởi nhu cầu của env.py,
# có thể được lấy:
# my_important_option = config.get_main_option("my_important_option")
# ... v.v.

def run_migrations_offline() -> None:
    """Chạy migration ở chế độ 'offline'.

    Điều này cấu hình ngữ cảnh chỉ với một URL
    và không có kết nối DBAPI thực sự.

    Bằng cách bỏ qua việc tạo Engine, chúng ta có thể chạy migration
    đối với một database trống hoặc đối với một database mà schema hiện tại
    đã được biết thông qua reflection.
    """
    # Lấy URL database từ settings của bạn
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    # Cấu hình ngữ cảnh với kết nối và metadata mục tiêu
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Chạy migration ở chế độ 'online'.

    Trong kịch bản này, chúng ta cần tạo một Engine
    và liên kết một kết nối với ngữ cảnh.
    """
    # MỚI: Dùng create_async_engine() để tạo engine bất đồng bộ
    connectable = create_async_engine(
        settings.DATABASE_URL, # Truyền URL trực tiếp
        # poolclass=pool.NullPool, # Tùy chọn: Sử dụng NullPool nếu không muốn giữ kết nối trong pool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    # MỚI: Đảm bảo engine được đóng sau khi sử dụng
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # MỚI: Chạy hàm async trong top-level khi Alembic gọi
    asyncio.run(run_migrations_online())
