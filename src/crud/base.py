# app/crud/base.py
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def get(self, obj_id: int, session: AsyncSession):
        return await session.get(self.model, obj_id)

    async def get_multi(self, session: AsyncSession):
        stmt = select(self.model)
        res = await session.execute(stmt)
        return list(res.scalars())

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
        await session.flush()
        return db_obj

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

        # для M2M/отношений обновление делается снаружи (не тут)
        await session.flush()
        return db_obj
