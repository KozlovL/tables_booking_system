from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.cafe import Cafe
from src.models.table import TableModel
from src.schemas.table import TableCreate, TableUpdate


class TableCRUD:

    def _build_query(
        self,
        cafe_id: int,
        table_id: Optional[int] = None,
        include_inactive: bool = False
    ):
        """Базовый запрос для получения столов в кафе"""
        query = select(TableModel).options(
            selectinload(TableModel.cafe)
            ).where(
                TableModel.cafe_id == cafe_id
            )
        if table_id is not None:
            query = query.where(TableModel.id == table_id)
        if not include_inactive:
            query = query.join(Cafe, TableModel.cafe_id == Cafe.id).where(
                TableModel.active.is_(True),
                Cafe.active.is_(True)
            )

        return query

    async def get_by_id_and_cafe(
        self,
        session: AsyncSession,
        table_id: int,
        cafe_id: int,
        include_inactive: bool = False
    ) -> TableModel:
        query = self._build_query(
            cafe_id=cafe_id,
            table_id=table_id,
            include_inactive=include_inactive
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def get_multi_by_cafe(
        self,
        session: AsyncSession,
        cafe_id: int,
        include_inactive: bool = False
    ) -> List[TableModel]:
        query = self._build_query(
            cafe_id=cafe_id,
            include_inactive=include_inactive
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self,
        session: AsyncSession,
        cafe_id: int,
        obj_in: TableCreate
    ) -> TableModel:
        db_obj = TableModel(**obj_in.model_dump(), cafe_id=cafe_id)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        result = await session.execute(
            select(TableModel)
            .options(selectinload(TableModel.cafe).selectinload(Cafe.managers))
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
        await session.commit()
        await session.refresh(db_obj)
        result = await session.execute(
            select(TableModel)
            .options(selectinload(TableModel.cafe).selectinload(Cafe.managers))
            .where(TableModel.id == db_obj.id)
        )
        return result.scalar_one()


table_crud = TableCRUD()
