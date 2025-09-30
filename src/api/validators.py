from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.table import table_crud
from src.models.table import TableModel
from src.models.cafe import Cafe


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол или кафе не найдены'
            )
    return table


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    """Функция проверки существования кафе"""
    exists_query = select(exists().where(Cafe.id == cafe_id))
    if not await session.scalar(exists_query):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено'
        )
