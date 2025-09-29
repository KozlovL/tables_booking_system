from sqlalchemy import String, Text, CheckConstraint, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, TimestampMixin, ActiveMixin


class Dish(Base, TimestampMixin, ActiveMixin):
    """Модель блюда."""
    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', name='fk_dish_cafe_id'),
        nullable=False
    )
    cafe: Mapped['Cafe'] = relationship('Cafe', back_populates='dishes')
    name: Mapped[str] = mapped_column(
        String(64),
        CheckConstraint('length(name) > 0', name='ck_dish_name_length'),
        unique=True,
        nullable=False
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text)
    photo: Mapped[str | None] = mapped_column(Text)

    def __repr__(self):
        return (
            f'Название блюда - {self.name}. '
            f'Цена блюда - {self.price}. '
            f'Описание блюда - {self.description[:30]}. '
        )
