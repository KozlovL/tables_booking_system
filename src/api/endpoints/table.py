from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.auth import get_current_user, require_admin
from src.crud.table import table_crud
from src.schemas.table import Table, TableCreate, TableUpdate
from src.models.user import User
from src.models.table import TableModel
from src.models.cafe import Cafe

router = APIRouter(prefix='/cafe/{cafe_id}/tables', tags=['Столы'])


@router.get(
    '',
    response_model=list[Table],
    summary='Получение списка столов в кафе'
)
async def get_tables_in_cafe(
    cafe_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> list[Table]:
#    include_inactive = current_user.role in ['admin', ' manager']
    await cafe_exists(cafe_id, session)
    tables = await table_crud.get_multi_by_cafe(
        session, cafe_id  # include_inactive
    )
    return tables


@router.post(
    '',
    response_model=Table,
    status_code=status.HTTP_201_CREATED,
    summary='Создание стола в кафе'
)
async def create_table(
    cafe_id: int,
    table_in: TableCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
) -> Table:
    await cafe_exists(cafe_id, session)
    table = await table_crud.create(session, cafe_id, table_in)
    await session.commit()
    return table


@router.get(
    '/{table_id}',
    response_model=Table,
    summary='Получение стола по ID'
)
async def get_table_by_id(
    cafe_id: int,
    table_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
) -> Table:
    table = await get_table_or_404(session, table_id, cafe_id)
    check_table_visibility_for_user(table, current_user)
    return table


@router.patch(
    '/{table_id}',
    response_model=Table,
    summary='Обновление стола по ID'
)
async def update_table(
    cafe_id: int,
    table_id: int,
    table_in: TableUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    table = await get_table_or_404(session, table_id, cafe_id)

    updated_table = await table_crud.update(session, table, table_in)
    await session.commit()
    return updated_table


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
    if current_user.role == 'user' and not table.active:
        raise HTTPException(status_code=404, detail='Стол или кафе не найдены')


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    cafe = await session.execute(
        select(Cafe.id).where(Cafe.id == cafe_id)
    )
    if cafe.scalar() is None:
        raise HTTPException(status_code=404, detail='Кафе не найдено')
