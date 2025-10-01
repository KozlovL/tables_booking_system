from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.core.types import PhoneNumber
from src.schemas.user import UserShort


class CafeCreate(BaseModel):
    """Схема для создания Кафе"""

    name: str
    address: str
    phone: PhoneNumber
    description: Optional[str] = None
    photo: Optional[str] = None              # base64 строка
    managers: List[int] = []                 # список ID менеджеров


class CafeRead(BaseModel):
    """Схема выдачи кафе наружу"""

    id: int
    name: str
    address: str
    phone: PhoneNumber
    description: Optional[str] = None
    photo: Optional[str] = None
    active: bool
    managers: List[UserShort]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CafeUpdate(BaseModel):
    """Схема обновления Кафе"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    address: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[PhoneNumber] = None          # у тебя может быть regex
    description: Optional[str] = None
    photo: Optional[str] = None          # base64 или None (стереть)
    managers: Optional[List[int]] = None # если передано — переопределяем список
    active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class CafeShort(BaseModel):
    """Схема выдачи кафе наружу кратко"""

    id: int
    name: str
    address: str
    phone: PhoneNumber
    description: Optional[str] = None
    photo: Optional[str] = None
    active: bool
    managers: List[UserShort]
    model_config = ConfigDict(from_attributes=True)
