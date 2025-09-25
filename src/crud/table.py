from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.table import TableModel
from src.schemas.table import TableCreate, TableUpdate


class TableCRUD:

    async def get_by_id_and_cafe(
        self,
        session: AsyncSession,
        table_id: int,
        cafe_id: int
    ) -> TableModel:
        table = (
            select(TableModel)
            .options(selectinload(TableModel.cafe))
            .where(
                TableModel.id == table_id,
                TableModel.cafe_id == cafe_id
            )
        )
        result = await session.execute(table)
        return result.scalars().first()

    async def get_multi_by_cafe(
        self,
        session: AsyncSession,
        cafe_id: int,
        include_inactive: bool = False
    ) -> List[TableModel]:
        tables = select(
            TableModel
        ).options(selectinload(TableModel.cafe)).where(
            TableModel.cafe_id == cafe_id
        )
        if not include_inactive:
            tables = tables.where(TableModel.active.is_(True))
        result = await session.execute(tables)
        return result.scalars().all()

    async def create(
        self,
        session: AsyncSession,
        cafe_id: int,
        obj_in: TableCreate
    ) -> TableModel:
        db_obj = TableModel(**obj_in.model_dump(), cafe_id=cafe_id)
        session.add(db_obj)
        await session.flush()
        result = await session.execute(
            select(TableModel)
            .options(selectinload(TableModel.cafe))
            .where(TableModel.id == db_obj.id)
        )
        return result.scalar_one()

    async def update(
        self,
        session: AsyncSession,
        db_obj: TableModel,
        obj_in: TableUpdate
    ) -> TableModel:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.flush()
        result = await session.execute(
            select(TableModel)
            .options(selectinload(TableModel.cafe))
            .where(TableModel.id == db_obj.id)
        )
        return result.scalar_one()


table_crud = TableCRUD()
