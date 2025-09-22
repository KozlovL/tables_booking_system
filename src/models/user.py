from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable


from src.models.cafe import cafe_managers_table
from src.core.db import Base, TimestampMixin, ActiveMixin


class User(SQLAlchemyBaseUserTable[int], Base, TimestampMixin, ActiveMixin):
    """Модель пользователя для базы данных."""

    __tablename__ = "user"  # Явно указываем имя таблицы (важно для Alembic)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(
        String(128), unique=False, index=False, nullable=True
    )

    email: Mapped[str] = mapped_column(
        String(320), unique=True, index=True, nullable=False
    )

    phone: Mapped[str | None] = mapped_column(
        String(32), unique=True, index=True, nullable=True
    )

    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)

    tg_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)

    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Связь многие-ко-многим: пользователь ↔ кафе
    managed_cafes = relationship(
        "Cafe",
        secondary=cafe_managers_table,
        back_populates="managers",
        lazy="selectin"  # ускорит выборку менеджеров вместе с кафе
    )


