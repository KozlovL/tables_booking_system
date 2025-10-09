from datetime import datetime
from enum import IntEnum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.cafe import CafeShort
from src.schemas.dish import Dish
from src.schemas.slot import TimeSlotShort
from src.schemas.table import TableShort
from src.schemas.user import UserShort


class BookingStatus(IntEnum):
    """Статусы бронирования."""

    BOOKED = 0
    CANCELLED = 1
    ACTIVE = 2


class BookingBase(BaseModel):
    """Базовая схема бронирования."""

    cafe_id: int = Field(..., description='ID кафе')
    guests_number: int = Field(..., ge=1, description='Количество гостей')
    note: Optional[str] = Field(None, description='Примечание к бронированию')


class BookingCreate(BookingBase):
    """Схема для создания бронирования."""

    tables: List[int] = Field(..., description='Бронируемые столы')
    slots: List[int] = Field(..., description='Слоты бронирования')
    menu: Optional[List[int]] = Field(
        [], description='Блюда для предварительного заказа')


class BookingUpdate(BaseModel):
    """Схема для обновления бронирования."""

    tables: Optional[List[int]] = Field(None, description='Бронируемые столы')
    slots: Optional[List[int]] = Field(None, description='Слоты бронирования')
    menu: Optional[List[int]] = Field(
        None, description='Блюда для предварительного заказа')
    guests_number: Optional[int] = Field(
        None, ge=1, description='Количество гостей')
    status: Optional[BookingStatus] = Field(
        None, description='Статус бронирования')
    note: Optional[str] = Field(None, description='Примечание к бронированию')
    active: Optional[bool] = Field(None, description='Активно ли бронирование')


class BookingShort(BaseModel):
    """Краткая схема бронирования."""

    id: int = Field(..., description='ID бронирования')
    user: UserShort = Field(..., description='Пользователь')
    cafe: CafeShort = Field(..., description='Кафе')
    tables: List[TableShort] = Field(..., description='Забронированные столы')
    slots: List[TimeSlotShort] = Field(..., description='Время бронирования')
    guests_number: int = Field(..., description='Количество гостей')
    status: BookingStatus = Field(..., description='Статус бронирования')
    active: bool = Field(..., description='Активно ли бронирование')

    model_config = ConfigDict(from_attributes=True)


class Booking(BookingShort):
    """Полная схема бронирования."""

    menu: List[Dish] = Field(...,
                             description='Блюда для предварительного заказа')
    note: Optional[str] = Field(None, description='Комментарий к бронированию')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    model_config = ConfigDict(from_attributes=True)
