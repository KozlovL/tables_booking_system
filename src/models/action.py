from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin


class Action(Base, TimestampMixin, ActiveMixin):
    """Модель акции."""

    __tablename__ = "actions"

    cafe_id: Mapped[int] = mapped_column(ForeignKey("cafe.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    cafe = relationship("Cafe", back_populates="actions")
