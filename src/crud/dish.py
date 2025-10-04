from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import Dish, Cafe


class CRUDDish(CRUDBase):
    async def create(self,
                     obj_in,
                     session: AsyncSession,
                     *,
                     exclude_fields: set[str] | None = None,
                     **extra_fields,
                     ):
        data = obj_in.model_dump(exclude_unset=True) if (
            hasattr(obj_in, "model_dump")) else dict(obj_in)
        if exclude_fields:
            for f in exclude_fields:
                data.pop(f, None)
        if extra_fields:
            data.update(extra_fields)
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        # Подгружаем связи
        result = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.cafe).selectinload(Cafe.managers)
            )
            .where(self.model.id == db_obj.id)
        )
        return result.scalar_one()

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
        updatable_fields: Iterable[str] | None = None,
    ):
        data = (
            obj_in.model_dump(exclude_unset=True)) \
            if hasattr(obj_in, "model_dump") else dict(obj_in)

        # ограничим обновление только колонками модели
        cols = {c.name for c in db_obj.__table__.columns}
        if updatable_fields is not None:
            cols &= set(updatable_fields)

        for field, value in data.items():
            if field in cols:
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        # Подгружаем связи
        result = await session.execute(
            select(self.model)
            .options(
                selectinload(self.model.cafe).selectinload(Cafe.managers)
            )
            .where(self.model.id == db_obj.id)
        )
        return result.scalar_one()


dish_crud = CRUDDish(Dish)