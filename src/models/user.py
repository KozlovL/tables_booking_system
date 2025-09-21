from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from src.core.db import Base
from src.core.constants import (
    USERNAME_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    TG_ID_MAX_LENGTH
)


CURRENT_DATE = datetime.now(timezone.utc)


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя для базы данных."""

    username = Column(String(USERNAME_MAX_LENGTH), nullable=False, index=True)
    phone = Column(String(PHONE_MAX_LENGTH), nullable=False, unique=True)
    tg_id = Column(String(TG_ID_MAX_LENGTH), nullable=True, unique=True)
    created_at = Column(DateTime, default=CURRENT_DATE, nullable=False)
    updated_at = Column(
        DateTime,
        default=CURRENT_DATE,
        onupdate=CURRENT_DATE,
        nullable=False
    )
