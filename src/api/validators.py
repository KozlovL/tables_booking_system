from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.table import table_crud
from src.models.table import TableModel
from src.models.cafe import Cafe, cafe_managers_table


async def get_table_or_404(
    session: AsyncSession,
    table_id: int,
    cafe_id: int,
    include_inactive: bool
) -> TableModel:
    """Проверка существования объекта с cafe_id, table_id"""

    table = await table_crud.get_by_id_and_cafe(
        session, table_id, cafe_id, include_inactive
    )
    if not table:
        raise HTTPException(status_code=404, detail='Стол или кафе не найдены')
    return table


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    """Функция проверки существования кафе"""
    cafe = await session.execute(
        select(Cafe.id).where(Cafe.id == cafe_id)
    )
    if cafe.scalar() is None:
        raise HTTPException(status_code=404, detail='Кафе не найдено')
