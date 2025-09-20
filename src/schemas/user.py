from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from fastapi_users import schemas

from src.core.constants import (
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    PHONE_MAX_LENGTH,
    PHONE_MIN_LENGTH,
    TG_ID_MAX_LENGTH
)


class UserRead(schemas.BaseUser[int]):
    """Схема для получения пользователя."""

    username: str
    phone: str
    tg_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания пользователя."""

    username: str = Field(min_length=USERNAME_MIN_LENGTH, 
                          max_length=USERNAME_MAX_LENGTH)
    phone: str = Field(min_length=PHONE_MIN_LENGTH,
                       max_length=PHONE_MAX_LENGTH)
    tg_id: Optional[str] = Field(None, max_length=TG_ID_MAX_LENGTH)


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для обновления пользователя."""

    username: Optional[str] = Field(None,
                                    min_length=USERNAME_MIN_LENGTH,
                                    max_length=USERNAME_MAX_LENGTH)
    phone: Optional[str] = Field(None,
                                 min_length=PHONE_MIN_LENGTH,
                                 max_length=PHONE_MAX_LENGTH)
    tg_id: Optional[str] = Field(None, max_length=TG_ID_MAX_LENGTH)


class UserShort(BaseModel):
    """Краткая схема пользователя для вложенных объектов."""

    id: int
    username: str
    email: Optional[str] = None
    phone: str
    is_active: bool
