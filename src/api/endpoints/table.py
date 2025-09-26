from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.auth import get_current_user, require_admin
from src.crud.table import table_crud
from src.api.validators import (
    get_table_or_404,
    cafe_exists,
    manager_or_admin_access
)
from src.schemas.table import Table, TableCreate, TableUpdate
from src.models.user import User

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
    include_inactive = await manager_or_admin_access(
        cafe_id, current_user, session
    )
    tables = await table_crud.get_multi_by_cafe(
        session, cafe_id, include_inactive
    )
    await cafe_exists(cafe_id, session)
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

    table = await get_table_or_404(
        session, table_id, cafe_id, current_user
    )
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
