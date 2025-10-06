from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.core.db import get_async_session
from src.core.auth import get_current_user
from src.api.deps.access import can_view_inactive, require_manager_or_admin
from src.models.user import User
from src.models.booking import BookingModel
from src.crud.booking import CRUDBooking
from src.schemas.booking import Booking, BookingCreate, BookingUpdate


router = APIRouter(prefix='/booking', tags=['Бронирование'])
crud_booking = CRUDBooking()


@router.get(
    '/',
    response_model=List[Booking],
    summary='Получить список бронирований',
    description='Получить список бронирований с фильтрацией'
)
async def get_bookings(
    show_all: Optional[bool] = Query(None,
                                     description='Показать все бронирования (для админа и менеджера)'),
    cafe_id: Optional[int] = Query(None,
                                   description='Показать бронирования в кафе'),
    user_id: Optional[int] = Query(None,
                                   description='Показать бронирования пользователя'),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    stmt = select(BookingModel)

    if user.is_superuser:
        if not show_all:
            stmt = stmt.where(BookingModel.active)
    else:
        is_manager = False
        managed_cafe_ids = []

        if user.managed_cafes:
            is_manager = True
            managed_cafe_ids = [cafe.id for cafe in user.managed_cafes]

        if is_manager:
            stmt = stmt.where(BookingModel.cafe_id.in_(managed_cafe_ids))
            if not show_all:
                stmt = stmt.where(BookingModel.active)
        else:
            stmt = stmt.where(
                and_(
                    BookingModel.user_id == user.id,
                    BookingModel.active
                )
            )

    if cafe_id:
        stmt = stmt.where(BookingModel.cafe_id == cafe_id)

    if user_id:
        if user.is_superuser:
            stmt = stmt.where(BookingModel.user_id == user_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав для фильтрации по пользователям'
            )

    result = await session.execute(stmt)
    bookings = list(result.scalars().all())

    return bookings


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
    booking = await crud_booking.get(booking_id, session)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Бронирование не найдено'
        )

    if user.is_superuser:
        return booking

    is_manager_of_cafe = can_view_inactive(booking.cafe_id, user)

    if is_manager_of_cafe:
        return booking

    if booking.user_id == user.id:
        if not booking.active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Бронирование не найдено'
            )
        return booking

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Недостаточно прав для просмотра этого бронирования'
    )


@router.post(
    '/',
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

    has_conflict = await crud_booking.check_booking_conflicts(
        session,
        booking_in.tables,
        booking_in.slots,
        booking_in.booking_date
    )

    if has_conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Выбранные столы или время уже заняты'
        )

    booking_data = booking_in.model_dump()
    booking_data['user_id'] = user.id

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
    booking = await crud_booking.get(booking_id, session)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Бронирование не найдено'
        )

    if user.is_superuser:
        pass
    else:
        try:
            require_manager_or_admin(booking.cafe_id, user)
            is_manager_of_cafe = True
        except HTTPException:
            is_manager_of_cafe = False

        if not is_manager_of_cafe and booking.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Недостаточно прав для редактирования этого бронирования'
            )

    if booking.booking_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя изменять прошедшие бронирования'
        )

    if booking_in.tables or booking_in.slots:
        tables_ids = booking_in.tables or [table.id for table in booking.tables]
        slots_ids = booking_in.slots or [slot.id for slot in booking.slots]
        booking_date = booking_in.booking_date or booking.booking_date

        has_conflict = await crud_booking.check_booking_conflicts(
            session,
            tables_ids,
            slots_ids,
            booking_date,
            exclude_booking_id=booking_id
        )

        if has_conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Выбранные столы или время уже заняты'
            )

    updated_booking = await crud_booking.update(booking, booking_in, session)
    return updated_booking
