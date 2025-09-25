
# src/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.core.types import PhoneNumber


# Короткая версия для отдачи наружу
class UserShort(BaseModel):
    """Схема данные юзера для отдачи наружу"""

    id: int
    username: str                 # required
    phone: str                    # required
    active: bool                  # required
    email: EmailStr | None = None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Схема создания пользователя."""
    
    username: str = Field(..., min_length=3, max_length=128)
    phone: PhoneNumber # обязателен
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    tg_id: Optional[str] = None


class UserRead(BaseModel):
    """Схема выдачи полных данных по юзеру"""

    id: int
    username: str
    phone: str
    email: Optional[EmailStr] = None
    tg_id: Optional[str] = None
    active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Схема админ меняет данные пользователя"""

    username: Optional[str] = Field(None, min_length=3, max_length=128)
    email: Optional[EmailStr] = None
    phone: PhoneNumber = None
    tg_id: Optional[str] = None
    password: Optional[str] = None
    active: Optional[bool] = None
      
