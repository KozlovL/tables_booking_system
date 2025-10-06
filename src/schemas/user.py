# src/schemas/user.py
from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from src.core.types import PhoneNumber


# Короткая версия для отдачи наружу
class UserShort(BaseModel):
    """Схема данные юзера для отдачи наружу."""

    id: int
    username: str  # required
    phone: str  # required
    active: bool  # required
    email: EmailStr | None = None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Схема создания пользователя."""

    username: str = Field(..., min_length=3, max_length=128)
    phone: PhoneNumber  # type: ignore
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    tg_id: Optional[str] = None


class UserRead(BaseModel):
    """Схема выдачи полных данных по юзеру."""

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
    """Схема админ меняет данные пользователя."""

    username: str | None = Field(default=None, min_length=3, max_length=128)
    email: EmailStr | None = None
    phone: PhoneNumber | None = None
    tg_id: str | None = None
    password: str | None = None
    active: bool | None = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('username', 'password', 'tg_id', 'phone', mode='before')
    @classmethod
    def prevent_empty_str(cls, value: Any) -> Any | None:
        """
        Универсальный валидатор, который не позволяет передавать пустые строки
        для текстовых полей.
        """
        if isinstance(value, str) and len(value) == 0:
            raise ValueError("не может быть пустой строкой")
        return value

class UserUpdateByAdmin(BaseModel):
    """Схема админ меняет данные пользователя."""

    username: str | None = Field(default=None, min_length=3, max_length=128)
    email: EmailStr | None = None
    phone: PhoneNumber | None = None
    tg_id: str | None = None
    # password: str | None = None
    active: bool | None = None

    model_config = ConfigDict(extra='forbid')

    @field_validator('username',  'tg_id', 'phone', mode='before')
    @classmethod
    def prevent_empty_str(cls, value: Any) -> Any | None:
        """
        Универсальный валидатор, который не позволяет передавать пустые строки
        для текстовых полей.
        """
        if isinstance(value, str) and len(value) == 0:
            raise ValueError("не может быть пустой строкой")
        return value