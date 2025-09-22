# src/core/db.py
from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Boolean, Column, func, Integer, DateTime, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr, Mapped, mapped_column

from src.core.config import settings

naming_convention = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class PreBase:
    metadata = MetaData(naming_convention=naming_convention)

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

class ActiveMixin:
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

Base = declarative_base(cls=PreBase)


engine = create_async_engine(
    settings.database_url,   # или settings.DATABASE_URL — как у тебя в конфиге
    echo=False,              # при необходимости True для дебага
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,   # чтобы объекты не "протухали" после commit()
    autoflush=False,          # ручной контроль за flush()
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
