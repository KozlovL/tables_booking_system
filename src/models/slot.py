from sqlalchemy import ForeignKey, Time, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin


class TimeSlot(Base, TimestampMixin, ActiveMixin):
    __tablename__ = 'time_slots'

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id'), nullable=False, index=True
    )
    date: Mapped[str] = mapped_column(Date, nullable=False)
    start_time: Mapped[str] = mapped_column(Time, nullable=False)
    end_time: Mapped[str] = mapped_column(Time, nullable=False)
    cafe = relationship('Cafe', back_populates='time_slots')
