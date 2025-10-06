from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.logger import logger
from src.models import Cafe, TableModel
from src.schemas import TableCreate, TableUpdate


class TableCRUD:
    """CRUD для TableModel с логированием."""

    def _build_query(
        self,
        cafe_id: int,
        table_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> select:
        """Формирует запрос с фильтрацией по кафе и активности."""
        query = (
            select(TableModel)
            .options(selectinload(TableModel.cafe).selectinload(Cafe.managers))
            .where(TableModel.cafe_id == cafe_id)
        )
        if table_id is not None:
            query = query.where(TableModel.id == table_id)
        if not include_inactive:
            query = query.join(Cafe, TableModel.cafe_id == Cafe.id).where(
                TableModel.active.is_(True),
                Cafe.active.is_(True),
            )
        return query

    async def get_by_id_and_cafe(
        self,
        session: AsyncSession,
        table_id: int,
        cafe_id: int,
        include_inactive: bool = False,
    ) -> Optional[TableModel]:
        """Возвращает стол по ID, привязанный к кафе."""
        query = self._build_query(
            cafe_id=cafe_id,
            table_id=table_id,
            include_inactive=include_inactive,
        )
        result = await session.execute(query)
        table = result.scalars().first()
        if table:
            logger.info(f'Найден стол id={table.id} в кафе id={cafe_id}')
        return table

    async def get_multi_by_cafe(
        self,
        session: AsyncSession,
        cafe_id: int,
        include_inactive: bool = False,
    ) -> List[TableModel]:
        """Возвращает все столы кафе (активные по умолчанию)."""
        query = self._build_query(
            cafe_id=cafe_id,
            include_inactive=include_inactive,
        )
        result = await session.execute(query)
        tables = result.scalars().all()
        logger.info(f'Найдено {len(tables)} столов в кафе id={cafe_id}')
        return tables

    async def create(
        self,
        session: AsyncSession,
        cafe_id: int,
        obj_in: TableCreate,
    ) -> TableModel:
        """Создаёт новый стол с загруженными связями."""
        db_obj = TableModel(**obj_in.model_dump(), cafe_id=cafe_id)
        session.add(db_obj)
        await session.commit()
        result = await session.execute(
            select(TableModel)
            .options(selectinload(TableModel.cafe).selectinload(Cafe.managers))
            .where(TableModel.id == db_obj.id),
        )
        table = result.scalar_one()
        logger.info(f'Создан стол id={table.id} в кафе id={cafe_id}')
        return table

    async def update(
        self,
        session: AsyncSession,
        db_obj: TableModel,
        obj_in: TableUpdate,
    ) -> TableModel:
        """Обновляет стол и возвращает объект с загруженными связями."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        result = await session.execute(
            select(TableModel)
            .options(selectinload(TableModel.cafe).selectinload(Cafe.managers))
            .where(TableModel.id == db_obj.id),
        )
        table = result.scalar_one()
        logger.info(f'Обновлён стол id={table.id} в кафе id={table.cafe_id}')
        return table


table_crud = TableCRUD()