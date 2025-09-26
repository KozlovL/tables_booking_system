from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.table import table_crud
from src.models.table import TableModel
from src.models.cafe import Cafe
from src.models.user import User


async def get_table_or_404(
    session: AsyncSession,
    table_id: int,
    cafe_id: int
) -> TableModel:
    table = await table_crud.get_by_id_and_cafe(session, table_id, cafe_id)
    if not table:
        raise HTTPException(status_code=404, detail='Стол или кафе не найдены')
    return table


def check_table_visibility_for_user(
    table: TableModel,
    current_user: User
) -> None:
    if current_user.is_superuser is False and not table.active:  # Нужно будет доделать логику для менеджеров
        raise HTTPException(status_code=404, detail='Стол или кафе не найдены')


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    cafe = await session.execute(
        select(Cafe.id).where(Cafe.id == cafe_id)
    )
    if cafe.scalar() is None:
        raise HTTPException(status_code=404, detail='Кафе не найдено')
