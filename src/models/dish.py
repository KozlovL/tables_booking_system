from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin
from src.models.cafe import Cafe


class Dish(Base, TimestampMixin, ActiveMixin):
    """Модель блюда."""

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', name='fk_dish_cafe_id'),
        nullable=False,
    )
    cafe: Mapped['Cafe'] = relationship('Cafe', back_populates='dishes')
    name: Mapped[str] = mapped_column(
        String(64),
        CheckConstraint('length(name) > 0', name='ck_dish_name_length'),
        nullable=False,
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    photo: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint(
            'cafe_id',
            'name',
            name='uc_dish_cafe_id_name_unique'),
    )

    def __repr__(self) -> str:
        return (
            f'Название блюда - {self.name}. '
            f'Цена блюда - {self.price}. '
            f'Описание блюда - {self.description[:30]}. '
        )
