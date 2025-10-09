from datetime import date as date_type
from datetime import time

from sqlalchemy import Date, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin
from src.models.booking import BookingModel


class TimeSlot(Base, TimestampMixin, ActiveMixin):
    """Модель временных слотов для бронирования в кафе.

    Attributes:
        cafe_id: ID кафе, к которому относится слот
        date: Дата слота
        start_time: Время начала слота
        end_time: Время окончания слота
        description: Описание слота (опционально)
        cafe: Связь с моделью кафе
        bookings: Список бронирований, связанных с этим слотом

    """

    __tablename__ = 'time_slots'

    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafe.id'),
                                         nullable=False, index=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[str | None] = mapped_column(String,
                                                    nullable=True,
                                                    default=None)
    cafe = relationship('Cafe', back_populates='time_slots', lazy='selectin')
    bookings: Mapped[list['BookingModel']] = relationship(
        'BookingModel',
        secondary='booking_slots',
        back_populates='slots',
        lazy='selectin',
    )
