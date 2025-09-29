# app/crud/base.py
from typing import Iterable, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, undefer

from src.models import Cafe


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

    async def get_by_field(
            self,
            session: AsyncSession,
            many: bool = False,
            **kwargs: Any
    ):
        """
        Функция получения одного или нескольких объектов по полям.

        Примеры запроса:

        objects_by_name = object_crud.get_by_field(
            session=session,
            many=True,
            name='some_name'
        )

        single_object_by_slug = object_crud.get_by_slug(
            session=session,
            slug='some_name'
        """
        stmt = select(self.model).filter_by(**kwargs).options(
            undefer(self.model.updated_at),
            undefer(self.model.created_at),
        )
        # Если модель не кафе, то подгружаем менеджеров через cafe
        if self.model != Cafe:
            stmt = stmt.options(
                selectinload(self.model.cafe).selectinload(Cafe.managers)
            )
        result = await session.execute(stmt)
        scalars = result.scalars()
        return scalars.all() if many else scalars.first()
