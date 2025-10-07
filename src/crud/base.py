from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, undefer

from src.core.logger import logger
from src.models import Cafe


class CRUDBase:
    """Базовый CRUD для SQLAlchemy-моделей."""

    def __init__(self, model: type) -> None:
        """Инициализация с моделью."""
        self.model = model

    async def get(self, obj_id: int, session: AsyncSession) -> Any:
        """Возвращает объект по ID."""
        obj = await session.get(self.model, obj_id)
        logger.info(f'Получен объект {self.model.__name__} id={obj_id}')
        return obj

    async def get_multi(self, session: AsyncSession) -> list[Any]:
        """Возвращает все объекты модели."""
        stmt = select(self.model)
        res = await session.execute(stmt)
        objs = list(res.scalars())
        logger.info(f'Получено {len(objs)} объектов {self.model.__name__}')
        return objs

    async def create(
        self,
        obj_in: Any,
        session: AsyncSession,
        *,
        exclude_fields: set[str] | None = None,
        **extra_fields: Any,
    ) -> Any:
        """Создает объект модели."""
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, 'model_dump')
            else dict(obj_in)
        )
        if exclude_fields:
            for f in exclude_fields:
                data.pop(f, None)
        if extra_fields:
            data.update(extra_fields)
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.flush()
        logger.info(f'Создан объект {self.model.__name__} с данными {data}')
        return db_obj

    async def update(
        self,
        db_obj: Any,
        obj_in: Any,
        session: AsyncSession,
        updatable_fields: Iterable[str] | None = None,
    ) -> Any:
        """Обновляет объект модели."""
        data = (
            obj_in.model_dump(exclude_unset=True)
            if hasattr(obj_in, 'model_dump')
            else dict(obj_in)
        )
        cols = {c.name for c in db_obj.__table__.columns}
        if updatable_fields is not None:
            cols &= set(updatable_fields)
        for field, value in data.items():
            if field in cols:
                setattr(db_obj, field, value)
        await session.flush()
        logger.info(
            f'Обновлен объект {self.model.__name__} '
            f'id={getattr(db_obj, "id", None)} с полями {list(data.keys())}',
        )
        return db_obj

    async def get_by_field(
        self,
        session: AsyncSession,
        many: bool = False,
        extra_uploading: bool = False,
        **kwargs: Any,
    ) -> Any:
        """Возвращает объекты по указанным полям."""
        stmt = select(self.model).filter_by(**kwargs)
        if self.model != Cafe and extra_uploading:
            stmt = stmt.options(
                selectinload(self.model.cafe).selectinload(Cafe.managers),
                undefer(self.model.updated_at),
                undefer(self.model.created_at),
            )
        result = await session.execute(stmt)
        scalars = result.scalars()
        objs = scalars.all() if many else scalars.first()
        logger.info(
            f'Получено {"множество" if many else "один"} '
            f'объектов {self.model.__name__} по {kwargs}',
        )
        return objs
