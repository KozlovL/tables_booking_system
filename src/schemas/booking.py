from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import IntEnum

from src.schemas.user import UserShort
from src.schemas.cafe import CafeShort
from src.schemas.table import TableShort
from src.schemas.slot import TimeSlotShort
from src.schemas.dish import Dish


class BookingStatus(IntEnum):
    BOOKED = 0
    CANCELLED = 1
    ACTIVE = 2


class BookingBase(BaseModel):
    cafe_id: int = Field(..., description='ID кафе')
    booking_date: date = Field(..., description='Дата бронирования')
    guests_number: int = Field(..., ge=1, description='Количество гостей')
    note: Optional[str] = Field(None, description='Примечание к бронированию')


class BookingCreate(BookingBase):
    tables: List[int] = Field(..., description='Бронируемые столы')
    slots: List[int] = Field(..., description='Слоты бронирования')
    menu: Optional[List[int]] = Field([], description='Блюда для предварительного заказа')

    @model_validator(mode='after')
    def validate_booking_date_not_in_past(self):
        if self.booking_date < date.today():
            raise ValueError('Нельзя бронировать на прошедшие даты')
        return self


class BookingUpdate(BaseModel):
    tables: Optional[List[int]] = Field(None, description='Бронируемые столы')
    slots: Optional[List[int]] = Field(None, description='Слоты бронирования')
    menu: Optional[List[int]] = Field(None,
                                      description='Блюда для предварительного заказа')
    guests_number: Optional[int] = Field(None, ge=1,
                                         description='Количество гостей')
    status: Optional[BookingStatus] = Field(None,
                                            description='Статус бронирования')
    note: Optional[str] = Field(None, description='Примечание к бронированию')
    active: Optional[bool] = Field(None, description='Активно ли бронирование')


class BookingShort(BaseModel):
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
    menu: List[Dish] = Field(...,
                             description='Блюда для предварительного заказа')
    note: Optional[str] = Field(None, description='Комментарий к бронированию')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    model_config = ConfigDict(from_attributes=True)
