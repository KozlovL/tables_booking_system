from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import can_view_inactive, require_manager_or_admin
from src.api.validators import cafe_exists, get_table_or_404
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.core.logger import log_request, logger
from src.crud.table import table_crud
from src.models import User
from src.schemas.table import Table, TableCreate, TableUpdate

router = APIRouter(prefix='/cafe/{cafe_id}/tables', tags=['Столы'])


@log_request()
@router.get(
    '',
    response_model=list[Table],
    summary='Получение списка столов в кафе '
            '(только для администратора и менеджера, '
            'пользователь - только активные)',
)
async def get_tables_in_cafe(
    cafe_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> list[Table]:
    """Возвращает список столов в указанном кафе.

    Права доступа:
    - Все авторизованные пользователи могут просматривать активные столы/кафе.
    - Менеджеры кафе и администраторы видят также неактивные столы/кафе.

    """
    await cafe_exists(cafe_id, session)
    include_inactive = can_view_inactive(
        cafe_id, current_user,
    )
    tables = await table_crud.get_multi_by_cafe(
        session,
        cafe_id,
        include_inactive,
    )

    logger.info(
        'Получен список столов',
        username=current_user.username,
        user_id=current_user.id,
        details={'cafe_id': cafe_id, 'count': len(tables)},
    )
    return tables


@log_request()
@router.post(
    '',
    response_model=Table,
    status_code=status.HTTP_201_CREATED,
    summary='Создание стола в кафе (только для администратора и менеджера)',
)
async def create_table(
    cafe_id: int,
    table_in: TableCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Table:
    """Создает стол в указаном кафе.

    Права доступа:
    - Менеджер кафе или администратор.
    """
    await cafe_exists(cafe_id, session)
    require_manager_or_admin(cafe_id, current_user)
    table = await table_crud.create(session, cafe_id, table_in)

    logger.info(
        'Создан новый стол',
        username=current_user.username,
        user_id=current_user.id,
        details={'table_id': table.id, 'cafe_id': cafe_id},
    )
    return table


@log_request()
@router.get(
    '/{table_id}',
    response_model=Table,
    summary='Получение стола по ID '
            '(только для администратора и менеджера, '
            'пользователь - только активные)',
)
async def get_table_by_id(
    cafe_id: int,
    table_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Table:
    """Возвращает стол в указаном кафе по ID.

    Права доступа:
    - Все авторизованные пользователи могут просматривать активный стол/кафе.
    - Менеджеры кафе и администраторы видят также неактивный стол/кафе.
    """
    await cafe_exists(cafe_id, session)
    include_inactive = can_view_inactive(
        cafe_id, current_user,
    )
    table = await get_table_or_404(
        session,
        table_id,
        cafe_id,
        include_inactive,
    )

    logger.info(
        'Получен стол по ID',
        username=current_user.username,
        user_id=current_user.id,
        details={'table_id': table.id, 'cafe_id': cafe_id},
    )
    return table


@log_request()
@router.patch(
    '/{table_id}',
    response_model=Table,
    summary='Обновление стола по ID (только для администратора и менеджера)',
)
async def update_table(
    cafe_id: int,
    table_id: int,
    table_in: TableUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> Table:
    """Изменяет стол в указаном кафе.

    Права доступа:
    - Менеджер кафе или администратор.
    """
    await cafe_exists(cafe_id, session)
    require_manager_or_admin(cafe_id, current_user)
    table = await get_table_or_404(
        session,
        table_id,
        cafe_id,
        include_inactive=True,
    )
    updated_table = await table_crud.update(session, table, table_in)

    logger.info(
        'Обновлён стол',
        username=current_user.username,
        user_id=current_user.id,
        details={'table_id': updated_table.id, 'cafe_id': cafe_id},
    )
    return updated_table
