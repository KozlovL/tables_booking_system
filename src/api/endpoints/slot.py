from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps.access import require_manager_or_admin, get_include_inactive
from src.api.validators import cafe_exists
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.crud.slot import time_slot_crud
from src.models.user import User
from src.schemas.slot import TimeSlotCreate, TimeSlotRead, TimeSlotUpdate

router = APIRouter(
    prefix='/cafe/{cafe_id}/time_slots',
    tags=['Временные слоты']
)


@router.post(
    '',
    response_model=TimeSlotRead,
    status_code=status.HTTP_201_CREATED,
    summary=(
        'Создание временного слота в кафе '
        '(только для администратора и менеджера)'
    )
)
async def create_time_slot(
    cafe_id: int = Path(..., description='ID кафе'),
    slot_data: TimeSlotCreate = ...,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_manager_or_admin),
) -> TimeSlotRead:
    await cafe_exists(cafe_id, session)

    if slot_data.cafe_id != cafe_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cafe ID в пути и данных не совпадают'
        )

    time_conflict = await time_slot_crud.check_time_conflict(
        cafe_id, slot_data.date, slot_data.start_time,
        slot_data.end_time, session
    )
    if time_conflict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Слот времени конфликтует с существующим'
        )

    if slot_data.start_time >= slot_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время начала должно быть раньше времени окончания'
        )

    slot = await time_slot_crud.create(slot_data, session)
    await session.commit()
    await session.refresh(slot)
    return slot


@router.get(
    '',
    response_model=list[TimeSlotRead],
    summary=(
        'Получение списка временных слотов в кафе '
        '(только для администратора и менеджера, '
        'пользователь - только активные)'
    )
)
async def get_time_slots(
    cafe_id: int = Path(..., description='ID кафе'),
    date_param: date = Query(None, description='Дата в формате YYYY-MM-DD',
                             alias='date'),
    include_inactive: bool = Depends(get_include_inactive),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> list[TimeSlotRead]:
    await cafe_exists(cafe_id, session)

    if not date_param:
        date_param = date.today()

    if include_inactive:
        if date_param:
            slots = await time_slot_crud.get_multi_by_cafe_and_date(
                cafe_id, date_param, session, False
            )
        else:
            slots = await time_slot_crud.get_multi_by_cafe(cafe_id,
                                                           session, False)
    else:
        if date_param:
            slots = await time_slot_crud.get_multi_by_cafe_and_date(
                cafe_id, date_param, session, True
            )
        else:
            slots = await time_slot_crud.get_multi_by_cafe(cafe_id,
                                                           session, True)

    return slots


@router.get(
    '/{time_slot_id}',
    response_model=TimeSlotRead,
    summary=(
        'Получение временного слота по ID '
        '(только для администратора и менеджера, '
        'пользователь - только активные)'
    )
)
async def get_time_slot_by_id(
    cafe_id: int = Path(..., description='ID кафе'),
    time_slot_id: int = Path(..., description='ID временного слота'),
    include_inactive: bool = Depends(get_include_inactive),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
) -> TimeSlotRead:
    await cafe_exists(cafe_id, session)

    slot = await time_slot_crud.get_with_cafe(time_slot_id, session)
    if not slot or slot.cafe_id != cafe_id:
        raise HTTPException(status_code=404, detail='Слот не найден')

    if not slot.active and not include_inactive:
        raise HTTPException(status_code=404, detail='Слот не найден')

    return slot


@router.patch(
    '/{time_slot_id}',
    response_model=TimeSlotRead,
    summary=(
        'Обновление временного слота по ID '
        '(только для администратора и менеджера)'
    )
)
async def update_time_slot_by_id(
    cafe_id: int = Path(..., description='ID кафе'),
    time_slot_id: int = Path(..., description='ID временного слота'),
    slot_data: TimeSlotUpdate = ...,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_manager_or_admin),
) -> TimeSlotRead:
    await cafe_exists(cafe_id, session)

    slot = await time_slot_crud.get(time_slot_id, session)
    if not slot or slot.cafe_id != cafe_id:
        raise HTTPException(status_code=404, detail='Слот не найден')

    if slot_data.date or slot_data.start_time or slot_data.end_time:
        new_date = slot_data.date or slot.date
        new_start = slot_data.start_time or slot.start_time
        new_end = slot_data.end_time or slot.end_time

        time_conflict = await time_slot_crud.check_time_conflict(
            cafe_id, new_date, new_start, new_end, session,
            exclude_slot_id=time_slot_id
        )
        if time_conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Новое время конфликтует с существующим слотом'
            )

        if new_start >= new_end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Время начала должно быть раньше времени окончания'
            )

    slot = await time_slot_crud.update(slot, slot_data, session)
    await session.commit()
    await session.refresh(slot)
    return slot
