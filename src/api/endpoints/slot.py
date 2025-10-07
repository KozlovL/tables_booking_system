from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.validators import (
    cafe_exists, check_timeslot_intersections,
    get_timeslot_or_404,
    get_timeslot_or_404_with_relations
    )
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.core.logger import log_request, logger
from src.crud.slot import time_slot_crud
from src.models import User
from src.schemas import (
    TimeSlotCreate,
    TimeSlotRead,
    TimeSlotUpdate
)
from src.api.deps import can_view_inactive, require_manager_or_admin


router = APIRouter(
    prefix='/cafe/{cafe_id}/time_slots',
    tags=['Временные слоты'],
)


@log_request()
@router.post(
    '',
    response_model=TimeSlotRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создание временного слота (для администратора и менеджера)',
)
async def create_time_slot(
    cafe_id: int,
    slot_data: TimeSlotCreate = ...,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TimeSlotRead:
    """Создаем timeslot в cafe_id."""
    await cafe_exists(cafe_id, session)
    require_manager_or_admin(cafe_id, current_user)

    await check_timeslot_intersections(
        cafe_id=cafe_id,
        slot_date=slot_data.date,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
        session=session,
    )

    slot = await time_slot_crud.create(cafe_id, slot_data, session)
    logger.info(
        'Создан новый слот',
        username=current_user.username,
        user_id=current_user.id,
        details={'slot_id': slot.id, 'cafe_id': cafe_id},
    )
    return slot


@log_request()
@router.get(
    '',
    response_model=list[TimeSlotRead],
    summary='Получение списка временных слотов в кафе',
)
async def get_time_slots(
    cafe_id: int = Path(..., description='ID кафе'),
    date_param: date = Query(
        default_factory=lambda: date.today(),
        description=('Дата (YYYY-MM-DD), по умолчанию сегодня')
    ),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> list[TimeSlotRead]:
    """Получаем список timeslot в cafe_id"""
    await cafe_exists(cafe_id, session)
    include_inactive = can_view_inactive(
        cafe_id, current_user
    )
    slots = await time_slot_crud.get_multi_by_cafe_and_date(
        cafe_id=cafe_id,
        slot_date=date_param,
        session=session,
        include_inactive=include_inactive,
    )
    logger.info(
        'Получен список слотов',
        username=current_user.username,
        user_id=current_user.id,
        details={'cafe_id': cafe_id, 'count': len(slots)},
    )
    return slots


@log_request()
@router.get(
    '/{time_slot_id}',
    response_model=TimeSlotRead,
    summary='Получение временного слота по ID',
)
async def get_time_slot_by_id(
    cafe_id: int = Path(..., description='ID кафе'),
    time_slot_id: int = Path(..., description='ID временного слота'),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TimeSlotRead:
    """Получаем timeslot по id."""
    await cafe_exists(cafe_id, session)
    include_inactive = can_view_inactive(cafe_id, current_user)
    slot = await get_timeslot_or_404_with_relations(
        time_slot_id,
        cafe_id,
        session,
    )

    if not slot.active and not include_inactive:
        raise HTTPException(status_code=404, detail='Слот не найден')

    logger.info(
        'Получен слот по ID',
        username=current_user.username,
        user_id=current_user.id,
        details={'slot_id': slot.id, 'cafe_id': cafe_id},
    )
    return slot


@log_request()
@router.patch(
    '/{time_slot_id}',
    response_model=TimeSlotRead,
    summary='Обновление временного слота (администратор и менеджер)',
)
async def update_time_slot_by_id(
    cafe_id: int = Path(..., description='ID кафе'),
    time_slot_id: int = Path(..., description='ID временного слота'),
    slot_data: TimeSlotUpdate = ...,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TimeSlotRead:
    """Обновляем timeslot по id."""
    await cafe_exists(cafe_id, session)
    require_manager_or_admin(cafe_id, current_user)
    slot = await get_timeslot_or_404(time_slot_id, session)
    update_data = slot_data.model_dump(exclude_unset=True)

    new_date = update_data.get('date', slot.date)
    new_start = update_data.get('start_time', slot.start_time)
    new_end = update_data.get('end_time', slot.end_time)

    time_changed = any(
        k in update_data for k in ('date', 'start_time', 'end_time')
    )
    if time_changed:
        now = datetime.now()
        original_dt = datetime.combine(slot.date, slot.start_time)
        new_dt = datetime.combine(new_date, new_start)

        if original_dt >= now and new_dt < now:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Нельзя изменить слот так, чтобы он оказался в прошлом'
            )

        await check_timeslot_intersections(
            cafe_id=cafe_id,
            slot_date=new_date,
            start_time=new_start,
            end_time=new_end,
            timeslot_id=time_slot_id,
            session=session,
        )

    slot = await time_slot_crud.update(slot, slot_data, session)
    logger.info(
        'Обновлён слот',
        username=current_user.username,
        user_id=current_user.id,
        details={'slot_id': slot.id, 'cafe_id': cafe_id},
    )
    return slot
