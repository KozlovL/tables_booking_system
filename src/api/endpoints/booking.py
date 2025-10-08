from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.db import get_async_session
from src.core.auth import get_current_user
from src.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
    PermissionDeniedError,
)
from src.api.deps import (
    can_view_inactive_booking,
    can_edit_booking
)
from src.models import BookingModel, User
from src.crud.booking import CRUDBooking
from src.schemas.booking import Booking, BookingCreate, BookingUpdate
from src.api.validators import (
    cafe_exists_and_acitve,
    validate_dish_for_booking,
    validate_slot_for_booking,
    validate_table_for_booking,
)

router = APIRouter(prefix='/booking', tags=['Бронирование'])
crud_booking = CRUDBooking()


@router.get(
    '',
    response_model=List[Booking],
    summary='Получить список бронирований',
    description='Получить список бронирований с фильтрацией'
)
async def get_bookings(
    show_all: Optional[bool] = Query(
        None,
        description='Показать все бронирования (для админа и менеджера)',
    ),
    cafe_id: Optional[int] = Query(
        None,
        description='Показать бронирования в кафе',
    ),
    user_id: Optional[int] = Query(
        None,
        description='Показать бронирования пользователя',
    ),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    if not (user.is_superuser or user.managed_cafe_ids):
        raise PermissionDeniedError()

    stmt = (
        select(BookingModel)
        .options(
            selectinload(BookingModel.user),
            selectinload(BookingModel.cafe),
            selectinload(BookingModel.tables),
            selectinload(BookingModel.slots),
            selectinload(BookingModel.menu),
        )
    )

    if cafe_id is not None:
        if user.is_superuser:
            stmt = stmt.where(BookingModel.cafe_id == cafe_id)
        else:
            if cafe_id not in user.managed_cafe_ids:
                raise PermissionDeniedError()
            stmt = stmt.where(BookingModel.cafe_id == cafe_id)
    else:
        if not user.is_superuser:
            stmt = stmt.where(BookingModel.cafe_id.in_(user.managed_cafe_ids))

    if user_id is not None:
        stmt = stmt.where(BookingModel.user_id == user_id)

    if not show_all:
        stmt = stmt.where(BookingModel.active.is_(True))

    result = await session.execute(stmt)
    return list(result.scalars().all())


@router.get(
    '/{booking_id}',
    response_model=Booking,
    summary='Получить бронирование по ID',
    description='Получить детальную информацию о бронировании'
)
async def get_booking(
    booking_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    booking = await crud_booking.get_with_relations(booking_id, session)
    if not booking:
        raise ResourceNotFoundError(
            'Бронирование'
        )

    if not booking.active and not can_view_inactive_booking(booking, user):
        raise ResourceNotFoundError(
            'Бронирование'
        )

    return booking


@router.post(
    '',
    response_model=Booking,
    status_code=status.HTTP_201_CREATED,
    summary='Создать новое бронирование',
    description='Создать новое бронирование стола'
)
async def create_booking(
    booking_in: BookingCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    await cafe_exists_and_acitve(
        booking_in.cafe_id,
        session,
    )
    await validate_table_for_booking(
        booking_in.tables,
        booking_in.cafe_id,
        booking_in.guests_number,
        session,
    )
    booking_date = await validate_slot_for_booking(
        booking_in.slots,
        booking_in.cafe_id,
        session,
    )
    await validate_dish_for_booking(
        booking_in.menu,
        booking_in.cafe_id,
        session,
    )
    has_conflict = await crud_booking.check_booking_conflicts(
        session,
        booking_in.cafe_id,
        booking_in.tables,
        booking_in.slots,
        booking_date,
    )

    if has_conflict:
        raise ConflictError(
            detail='Выбранные столы или время уже заняты'
        )

    booking_data = booking_in.model_dump()
    booking_data['user_id'] = user.id
    booking_data['booking_date'] = booking_date

    booking = await crud_booking.create(booking_data, session)
    return booking


@router.patch(
    '/{booking_id}',
    response_model=Booking,
    summary='Обновить бронирование',
    description='Обновить информацию о бронировании'
)
async def update_booking(
    booking_id: int,
    booking_in: BookingUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    booking = await crud_booking.get_with_relations(booking_id, session)

    if not booking:
        raise ResourceNotFoundError(
            'Бронирование'
        )

    if not can_edit_booking(booking, user):
        raise PermissionDeniedError(
            detail='Недостаточно прав для редактирования этого бронирования'
        )

    update_data = booking_in.model_dump(exclude_unset=True)
    cafe_id = update_data.get('cafe_id', booking.cafe_id)
    await cafe_exists_and_acitve(
        cafe_id,
        session,
    )

    tables_ids = update_data.get('tables', [t.id for t in booking.tables])
    slots_ids = update_data.get('slots', [s.id for s in booking.slots])

    if 'tables' in update_data:
        guests_number = update_data.get('guests_number', booking.guests_number)
        await validate_table_for_booking(
            table_ids=tables_ids,
            cafe_id=cafe_id,
            guests_number=guests_number,
            session=session,
        )

    if 'slots' in update_data:
        booking_date = await validate_slot_for_booking(
            slot_ids=slots_ids,
            cafe_id=cafe_id,
            session=session,
        )
        booking.booking_date = booking_date
    else:
        booking_date = booking.booking_date

    if 'menu' in update_data:
        dish_ids = update_data.get('menu', [d.id for d in booking.menu])
        await validate_dish_for_booking(
            dish_ids=dish_ids,
            cafe_id=cafe_id,
            session=session,
        )
    field_changed = any(
        k in update_data for k in ('tables', 'slots', 'cafe_id')
    )
    if field_changed:
        has_conflict = await crud_booking.check_booking_conflicts(
            session,
            cafe_id,
            tables_ids,
            slots_ids,
            booking_date,
            exclude_booking_id=booking_id
        )

        if has_conflict:
            raise ConflictError(
                detail='Выбранные столы или время уже заняты'
            )

    updated_booking = await crud_booking.update(booking, booking_in, session)
    return updated_booking
