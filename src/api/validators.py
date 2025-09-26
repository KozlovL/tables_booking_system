from fastapi import HTTPException
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.table import table_crud
from src.models.table import TableModel
from src.models.cafe import Cafe, cafe_managers_table
from src.models.user import User


async def get_table_or_404(
    session: AsyncSession,
    table_id: int,
    cafe_id: int,
    current_user: User
) -> TableModel:
    include_inactive = await manager_or_admin_access(
        cafe_id, current_user, session
    )
    table = await table_crud.get_by_id_and_cafe(
        session, table_id, cafe_id, include_inactive
    )
    if not table:
        raise HTTPException(status_code=404, detail='Стол или кафе не найдены')
    return table


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    cafe = await session.execute(
        select(Cafe.id).where(Cafe.id == cafe_id)
    )
    if cafe.scalar() is None:
        raise HTTPException(status_code=404, detail='Кафе не найдено')


async def manager_or_admin_access(
    cafe_id,
    current_user: User,
    session: AsyncSession
) -> bool:
    query = select(exists().where(
        cafe_managers_table.c.user_id == current_user.id,
        cafe_managers_table.c.cafe_id == cafe_id
    ))
    result = await session.execute(query)
    is_manager = result.scalar()
    return is_manager or current_user.is_superuser
