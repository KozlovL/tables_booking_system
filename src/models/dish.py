from sqlalchemy import ForeignKey, String, Text, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core.db import Base, TimestampMixin, ActiveMixin


class Dish(Base, TimestampMixin, ActiveMixin):
    """Модель блюда."""
    cafe: Mapped[int] = mapped_column(ForeignKey('cafe.id'), nullable=False)
    name: Mapped[str] = mapped_column(
        String(64),
        CheckConstraint('length(name) > 0'),
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
