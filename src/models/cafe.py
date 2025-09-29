from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin

#Определяем таблицу-связку
cafe_managers_table = Table(
    "cafe_managers",
    Base.metadata,
    Column("user_id",
           Integer,
           ForeignKey("user.id"), primary_key=True),
    Column("cafe_id",
           Integer,
           ForeignKey("cafe.id"), primary_key=True),
)


class Cafe(Base, TimestampMixin, ActiveMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128),
                                      index=True,
                                      unique=True,
                                      nullable=False,
                                      )
    address: Mapped[str] = mapped_column(String(255),
                                         index=True,
                                         nullable=False,
                                         )
    phone: Mapped[str | None] = mapped_column(String(32),
                                              index=True,
                                              nullable=False,
                                              )
    description: Mapped[str | None] = mapped_column(Text)
    photo: Mapped[str | None] = mapped_column(Text)
    managers = relationship(
        "User",
        secondary=cafe_managers_table,
        back_populates="managed_cafes",
        lazy="selectin",
    )
    dishes: Mapped[list['Dish']] = relationship(
        'Dish',
        back_populates='cafe'
    )
