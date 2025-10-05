from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import ActiveMixin, Base, TimestampMixin
from src.models.cafe import cafe_managers_table


class User(Base, TimestampMixin, ActiveMixin):
    # Base уже создаёт id PK
    username: Mapped[str] = mapped_column(String(128),
                                          unique=True,
                                          index=True,
                                          nullable=False,
                                          )
    email:    Mapped[str] = mapped_column(String(320),
                                          unique=True,
                                          index=True,
                                          nullable=True,
                                          )
    phone:    Mapped[str | None] = mapped_column(String(20),
                                                 unique=True,
                                                 index=True,
                                                 nullable=False,
                                                 doc = ("телефон "
                                                        "пользователя в"
                                                         "международном "
                                                        "формате "
                                                         "(+79991234567)"),
                                                 )
    hashed_password: Mapped[str] = mapped_column(String(1024),
                                                 nullable=False,
                                                 )
    tg_id: Mapped[str] = mapped_column(String(),
                                       unique=True,
                                       nullable=True,
                                       )
    is_superuser: Mapped[bool] = mapped_column(Boolean,
                                               default=False,
                                               nullable=False,
                                               )
    is_verified:  Mapped[bool] = mapped_column(Boolean,
                                               default=False,
                                               nullable=False,
                                               )
    # Связь многие-ко-многим: пользователь ↔ кафе
    managed_cafes = relationship(
        "Cafe",
        secondary=cafe_managers_table,
        back_populates="managers",
        lazy="selectin",  # ускорит выборку менеджеров вместе с кафе
    )