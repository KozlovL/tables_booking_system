from typing import AsyncGenerator

from sqlalchemy import Column, Integer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, declared_attr, sessionmaker

from src.core.config import settings


class PreBase:
    """Базовый класс для всех моделей SQLAlchemy."""

    @declared_attr
    def __tablename__(self) -> str:
        """Автоматически генерирует имя таблицы из имени класса."""
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=PreBase)
engine = create_async_engine(settings.database_url)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию SQLAlchemy."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
