from typing import Annotated

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from config import settings

DATABASE_URL = settings.DATABASE_URL


async_engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Hiển thị các lệnh SQL được thực thi (hữu ích cho debug)
    pool_pre_ping=True,
    pool_size=10, # Kích thước pool kết nối
    max_overflow=20, # Số lượng kết nối tối đa có thể vượt quá pool_size
)


AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


db_dependency = Annotated[AsyncSession, Depends(get_db)]


