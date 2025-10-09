from functools import cached_property
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin
from src.models.booking import BookingModel
from src.models.cafe import cafe_managers_table

if TYPE_CHECKING:
    from src.models.cafe import Cafe


class User(Base, TimestampMixin, ActiveMixin):
    """Модель пользователя с контактными данными, паролем и правами."""

    username: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=True,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        doc='Телефон пользователя в международном формате (+79991234567)',
    )
    hashed_password: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    tg_id: Mapped[str | None] = mapped_column(
        String(),
        unique=True,
        nullable=True,
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # Связь многие-ко-многим: пользователь ↔ кафе (менеджеры)
    managed_cafes: Mapped[list['Cafe']] = relationship(
        'Cafe',
        secondary=cafe_managers_table,
        back_populates='managers',
        lazy='selectin',
    )

    bookings: Mapped[list['BookingModel']] = relationship(
        'BookingModel',
        back_populates='user',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        return (
            f'User(username={self.username}, '
            f'phone={self.phone}, is_superuser={self.is_superuser}) '
        )

    @cached_property
    def managed_cafe_ids(self) -> set[int]:
        """Возвращает множество ID кафе, которыми управляет пользователь."""
        return {cafe.id for cafe in self.managed_cafes}
