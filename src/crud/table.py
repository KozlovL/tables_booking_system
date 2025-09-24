from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.table import TableModel
from src.schemas.table import TableCreate, TableUpdate


class TableCRUD:
    async def get_by_id_and_cafe(
        self,
        session: AsyncSession,
        table_id: int,
        cafe_id: int
    ) -> Optional[TableModel]:
        table = select(TableModel).where(
            TableModel.id == table_id,
            TableModel.cafe_id == cafe_id
        )
        result = await session.execute(table)
        return result.scalars().first()

    async def get_multi_by_cafe(
        self,
        session: AsyncSession,
        cafe_id: int,
        include_inactive: bool = False
    ) -> List[TableModel]:
        tables = select(TableModel).where(TableModel.cafe_id == cafe_id)
        if not include_inactive:
            tables = tables.where(TableModel.active.is_(True))
        result = await session.execute(tables)
        return result.scalars().all()

    async def create_by_cafe(
        self,
        session: AsyncSession,
        cafe_id: int,
        obj_in: TableCreate
    ) -> TableModel:
        db_obj = TableModel(**obj_in.model_dump(), cafe_id=cafe_id)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update_by_cafe(
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
        await session.refresh(db_obj)
        return db_obj


table_crud = TableCRUD()
