from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, AnyUrl, ConfigDict


# Короткая версия для отдачи наружу
class UserShort(BaseModel):
    id: int
    username: str                 # required
    phone: str                    # required
    active: bool                  # required
    email: EmailStr | None = None
    model_config = ConfigDict(from_attributes=True)


class CafeCreate(BaseModel):
    name: str
    address: str
    phone: str
    description: Optional[str] = None
    photo: Optional[str] = None              # base64 строка
    managers: List[int] = []                 # список ID менеджеров

class CafeRead(BaseModel):
    id: int
    name: str
    address: str
    phone: Optional[str] = None
    description: Optional[str] = None
    active: bool
    created_at: datetime
    updated_at: datetime
    managers: List[UserShort]
    model_config = ConfigDict(from_attributes=True)


