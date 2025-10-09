from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin

if TYPE_CHECKING:
    from src.models import BookingModel, Cafe


class TableModel(Base, TimestampMixin, ActiveMixin):
    """Модель стола в кафе с количеством мест и описанием."""

    __tablename__ = 'tables'

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id'),
        nullable=False,
    )
    seats_number: Mapped[int] = mapped_column(
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='tables',
        lazy='selectin',
        )
    bookings: Mapped[list['BookingModel']] = relationship(
        'BookingModel',
        secondary='booking_tables',
        back_populates='tables',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint('seats_number > 0', name='check_seats_positive'),
    )

    def __repr__(self) -> str:
        return (
            f'TableModel(cafe_id={self.cafe_id}, '
            f'seats_number={self.seats_number})'
        )
