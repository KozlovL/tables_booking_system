from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps.access import require_manager_or_admin, get_include_inactive
from src.api.validators import (
    cafe_exists, validate_and_check_conflicts,
    get_timeslot_or_404,
    get_timeslot_or_404_with_relations
    )
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.crud.slot import time_slot_crud
from src.models import User
from src.schemas import (
    TimeSlotCreate,
    TimeSlotRead,
    TimeSlotUpdate
)
from src.api.deps import get_include_inactive

router = APIRouter(
    prefix='/cafe/{cafe_id}/time_slots',
    tags=['Временные слоты'],
)


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
    await cafe_exists(cafe_id, session)
    await require_manager_or_admin(cafe_id, current_user, session)

    await validate_and_check_conflicts(
        cafe_id=cafe_id,
        slot_date=slot_data.date,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
        session=session,
    )

    slot = await time_slot_crud.create(cafe_id, slot_data, session)
    return slot


@router.get(
    '',
    response_model=list[TimeSlotRead],
    summary='Получение списка временных слотов в кафе',
)
async def get_time_slots(
    cafe_id: int = Path(..., description='ID кафе'),
    date_param: date = Query(default_factory=lambda: date.today(), description=(
        'Дата (YYYY-MM-DD), по умолчанию сегодня')),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> list[TimeSlotRead]:
    await cafe_exists(cafe_id, session)
    include_inactive = await get_include_inactive(
        cafe_id, current_user, session
    )
    slots = await time_slot_crud.get_multi_by_cafe_and_date(
        cafe_id=cafe_id,
        slot_date=date_param,
        session=session,
        include_inactive=include_inactive,
    )
    return slots


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
    await cafe_exists(cafe_id, session)
    include_inactive = await get_include_inactive(cafe_id, current_user, session)
    slot = await get_timeslot_or_404_with_relations(time_slot_id, session)

    if not slot.active and not include_inactive:
        raise HTTPException(status_code=404, detail='Слот не найден')

    return slot


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
    await cafe_exists(cafe_id, session)
    await require_manager_or_admin(cafe_id, current_user, session)
    slot = await get_timeslot_or_404(time_slot_id, session)

    new_date = (slot_data.date if
                slot_data.date is not None else slot.date)
    new_start = (slot_data.start_time if
                 slot_data.start_time is not None else slot.start_time)
    new_end = (slot_data.end_time if
               slot_data.end_time is not None else slot.end_time)

    await validate_and_check_conflicts(
        cafe_id=cafe_id,
        slot_date=new_date,
        start_time=new_start,
        end_time=new_end,
        session=session,
        exclude_slot_id=time_slot_id,
    )

    slot = await time_slot_crud.update(slot, slot_data, session)
    return slot