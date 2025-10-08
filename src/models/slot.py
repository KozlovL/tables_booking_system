from datetime import time, date as date_type
from sqlalchemy import ForeignKey, String, Time, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin


class TimeSlot(Base, TimestampMixin, ActiveMixin):
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
        lazy='selectin'
    )
