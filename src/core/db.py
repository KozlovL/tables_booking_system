from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Boolean, DateTime, MetaData, func
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    declared_attr,
    mapped_column,
)

from src.core.config import settings
from src.core.logger import logger

naming_convention = {
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
}


class PreBase:
    """Базовый класс для всех моделей SQLAlchemy."""

    metadata = MetaData(naming_convention=naming_convention)

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)


class TimestampMixin:
    """Добавляет поля created_at и updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ActiveMixin:
    """Добавляет поле active."""

    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


Base = declarative_base(cls=PreBase)

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронной сессии SQLAlchemy."""
    async with AsyncSessionLocal() as session:
        logger.debug('Создана новая сессия AsyncSession')
        yield session
