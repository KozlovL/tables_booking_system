# src/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr

PhoneNumber = constr(
    pattern=r'^\+?[1-9]\d{7,14}$',
    min_length=10,
    max_length=15,
)


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


# class UserUpdateMe(BaseModel):
#     """Схема польз сам меняет данные о себе, поле актив изменить нельзя """
#     username: Optional[str] = Field(None, min_length=3, max_length=128)
#     email: Optional[EmailStr] = None
#     phone: PhoneNumber = None
#     tg_id: Optional[str] = None
#     password: Optional[str] = None
#     active: bool


class UserUpdate(BaseModel):
    """Схема админ меняет данные пользователя"""

    username: Optional[str] = Field(None, min_length=3, max_length=128)
    email: Optional[EmailStr] = None
    phone: PhoneNumber = None
    tg_id: Optional[str] = None
    password: Optional[str] = None
    active: bool
