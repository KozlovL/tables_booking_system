from datetime import date
from enum import IntEnum

from sqlalchemy import Column, Date, ForeignKey, Table, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin


class BookingStatus(IntEnum):
    """Статусы бронирования."""

    BOOKED = 0
    CANCELLED = 1
    ACTIVE = 2


booking_tables_table = Table(
    'booking_tables',
    Base.metadata,
    Column('booking_id', ForeignKey('bookingmodel.id', ondelete='CASCADE'),
           primary_key=True),
    Column('table_id', ForeignKey('tables.id', ondelete='CASCADE'),
           primary_key=True),
)
"""Ассоциативная таблица для связи бронирований и столов."""


booking_slots_table = Table(
    'booking_slots',
    Base.metadata,
    Column('booking_id', ForeignKey('bookingmodel.id', ondelete='CASCADE'),
           primary_key=True),
    Column('slot_id', ForeignKey('time_slots.id', ondelete='CASCADE'),
           primary_key=True),
)
"""Ассоциативная таблица для связи бронирований и временных слотов."""


booking_dishes_table = Table(
    'booking_dishes',
    Base.metadata,
    Column('booking_id', ForeignKey('bookingmodel.id', ondelete='CASCADE'),
           primary_key=True),
    Column('dish_id', ForeignKey('dish.id', ondelete='CASCADE'),
           primary_key=True),
)
"""Ассоциативная таблица для связи бронирований и блюд."""


class BookingModel(Base, TimestampMixin, ActiveMixin):
    """Модель бронирования столов в кафе.

    Attributes:
        user_id: ID пользователя, создавшего бронирование
        cafe_id: ID кафе, где осуществляется бронирование
        booking_date: Дата бронирования
        guests_number: Количество гостей
        status: Статус бронирования
        note: Примечание к бронированию

    Relationships:
        user: Пользователь, создавший бронирование
        cafe: Кафе, где осуществляется бронирование
        tables: Забронированные столы
        slots: Временные слоты бронирования
        menu: Блюда для предварительного заказа

    """

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True,
    )
    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', ondelete='CASCADE'), nullable=False, index=True,
    )
    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    guests_number: Mapped[int] = mapped_column(nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus),
        default=BookingStatus.BOOKED,
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped['User'] = relationship(
        'User',
        back_populates='bookings',
        lazy='selectin',
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='bookings',
        lazy='selectin',
    )
    tables: Mapped[list['TableModel']] = relationship(
        'TableModel',
        secondary=booking_tables_table,
        back_populates='bookings',
        lazy='selectin',
    )
    slots: Mapped[list['TimeSlot']] = relationship(
        'TimeSlot',
        secondary=booking_slots_table,
        back_populates='bookings',
        lazy='selectin',
    )
    menu: Mapped[list['Dish']] = relationship(
        'Dish',
        secondary=booking_dishes_table,
        back_populates='bookings',
        lazy='selectin',
    )
