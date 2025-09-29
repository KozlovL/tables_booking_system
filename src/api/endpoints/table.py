from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_include_inactive, require_manager_or_admin
from src.api.deps.access import check_admin_or_manager
from src.core.db import get_async_session
from src.core.auth import get_current_user
from src.crud.table import table_crud
from src.api.validators import (
    get_table_or_404,
    cafe_exists,
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
    current_user: User = Depends(get_current_user),
    include_inactive: bool = Depends(get_include_inactive)
) -> list[Table]:
    """
    Возвращает список столов в указанном кафе.

    Права доступа:
    - Все авторизованные пользователи могут просматривать активные столы/кафе.
    - Менеджеры кафе и администраторы видят также неактивные столы/кафе.

    """
    await cafe_exists(cafe_id, session)
    tables = await table_crud.get_multi_by_cafe(
        session, cafe_id, include_inactive
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
    current_user: User = Depends(get_current_user)
):
    """
    Создает стол в указаном кафе.

    Права доступа:
    - Менеджер кафе или администратор.
    """
    await check_admin_or_manager(
        session=session,
        cafe_id=cafe_id,
        current_user=current_user,
    )
    await cafe_exists(cafe_id, session)
    table = await table_crud.create(session, cafe_id, table_in)
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
    current_user: User = Depends(get_current_user),
    include_inactive: bool = Depends(get_include_inactive)
) -> Table:
    """
    Возвращает стол в указаном кафе по ID

    Права доступа:
    - Все авторизованные пользователи могут просматривать активный стол/кафе.
    - Менеджеры кафе и администраторы видят также неактивный стол/кафе.
    """
    table = await get_table_or_404(
        session, table_id, cafe_id, include_inactive
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
    current_user: User = Depends(get_current_user)
) -> Table:
    """
    Изменяет стол в указаном кафе

    Права доступа:
    - Менеджер кафе или администратор.
    """
    await check_admin_or_manager(
        session=session,
        cafe_id=cafe_id,
        current_user=current_user,
    )
    table = await get_table_or_404(
        session, table_id, cafe_id, include_inactive=True
    )

    updated_table = await table_crud.update(session, table, table_in)
    return updated_table
