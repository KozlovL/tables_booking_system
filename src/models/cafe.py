from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin

if TYPE_CHECKING:
    from src.models.dish import Dish
    from src.models.table import TableModel
    from src.models.user import User

cafe_managers_table = Table(
    'cafe_managers',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('cafe_id', Integer, ForeignKey('cafe.id'), primary_key=True),
)


class Cafe(Base, TimestampMixin, ActiveMixin):
    """Модель кафе с менеджерами, блюдами и столами."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(128),
        index=True,
        unique=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )
    phone: Mapped[str | None] = mapped_column(
        String(32),
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text)
    photo: Mapped[str | None] = mapped_column(Text)

    managers: Mapped[list['User']] = relationship(
        'User',
        secondary=cafe_managers_table,
        back_populates="managed_cafes",
        lazy='joined',
    )

    dishes: Mapped[list['Dish']] = relationship(
        'Dish',
        back_populates='cafe',
    )

    tables: Mapped[list['TableModel']] = relationship(
        'TableModel',
        back_populates='cafe',
        lazy='selectin',
    )
    time_slots = relationship('TimeSlot', back_populates='cafe',
                              lazy='selectin')
    bookings: Mapped[list['BookingModel']] = relationship(
        'BookingModel',
        back_populates='cafe',
        lazy='selectin'
    )
