from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey,
from src.core.db import Base


class TableModel(Base):   #добавь миксины
    __tablename__ = 'tables'

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id'), nullable=False
    )
    seats_number: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

