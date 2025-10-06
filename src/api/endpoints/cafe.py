from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.auth import get_current_user, require_admin
from src.core.db import get_async_session
from src.core.exceptions import ResourceNotFoundError, PermissionDeniedError
from src.crud.cafe import cafe_crud
from src.core.logger import log_request, logger
from src.models.cafe import Cafe as CafeModel
from src.models.user import User
from src.schemas.cafe import CafeCreate, CafeRead, CafeUpdate

router = APIRouter(prefix='/cafes', tags=["Кафе"])


@log_request()
@router.post(
    '',
    response_model=CafeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
    summary='Создание кафе (только для администратора)',
    )
async def create_cafe(
    payload: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> CafeRead:
    """Создание кафе."""
    photo_url = payload.photo if payload.photo else None
    cafe = await cafe_crud.create_with_managers(
        payload,
        session,
        photo_url=photo_url,
    )

    logger.info(
        'Создано кафе',
        username=current_user.username,
        user_id=current_user.id,
        details={'cafe_id': cafe.id},
    )
    return cafe


@log_request()
@router.get(
    '',
    response_model=list[CafeRead],
    status_code=status.HTTP_200_OK,
    summary='Получение списка кафе '
            '(только для администратора, пользователь - только активные)',
    )
async def list_cafes(
    show_all: bool = Query(False,
                           description='Показать все кафе '
                                       '(Неактивные только для админа)',
                           ),
    limit: int | None = Query(None, ge=1),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> list[CafeRead]:
    # если пользователь не админ → всегда только активные
    """Получение списка кафе.

    (Только для администратора, пользователь - только активные).
    """
    only_active = True
    if current_user.is_superuser:
        only_active = not show_all

    cafes = await cafe_crud.get_multi_filtered(
        session,
        only_active=only_active,
    )

    logger.info(
        'Получен список кафе',
        username=current_user.username,
        user_id=current_user.id,
        details={'count': len(cafes), 'only_active': only_active},
    )
    return cafes


@log_request()
@router.get(
    '/{cafe_id}',
    response_model=CafeRead,
    status_code=status.HTTP_200_OK,
    summary='Получение кафе по ID '
            '(только для администратора, пользователь - только активные)',
)
async def get_cafe(
    cafe_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> CafeRead:
    """Возвращает кафе по ID с проверкой прав доступа."""
    stmt = (
        select(CafeModel)
        .options(selectinload(CafeModel.managers))   # <— ключевой момент
        .where(CafeModel.id == cafe_id)
    )

    res = await session.execute(stmt)
    cafe = res.scalar_one_or_none()

    if not cafe:
        raise ResourceNotFoundError("Кафе")
    if cafe.active or current_user.is_superuser:

        logger.info(
            'Получено кафе по ID',
            username=current_user.username,
            user_id=current_user.id,
            details={'cafe_id': cafe.id},
        )
        return cafe
    raise PermissionDeniedError()


@log_request()
@router.patch(
    '/{cafe_id}',
    response_model=CafeRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
    summary='Обновление кафе по ID (только для администратора)',
    )
async def update_cafe(
        cafe_id: int,
        payload: CafeUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(require_admin),
) -> CafeRead:
    """Обновление кафе по ID (только для администратора)."""
    cafe = await cafe_crud.get_with_managers(cafe_id, session)
    if not cafe:
        raise ResourceNotFoundError("Кафе")

        # 2. Обработка фото (base64 → путь)
    update_data = payload.model_dump(exclude_unset=True)
    photo_url = None
    if 'photo' in update_data and update_data['photo']:
            photo_url = update_data['photo']
    cafe = await cafe_crud.update_with_managers(
        cafe,
        payload,
        session,
        photo_url=photo_url,
        )
    logger.info(
            'Обновлено кафе по ID',
            username=current_user.username,
            user_id=current_user.id,
            details={'cafe_id': cafe.id},
    )
    return cafe

