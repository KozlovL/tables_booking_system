from datetime import date as date_type, datetime, time
from typing import Optional, Union
from pydantic import BaseModel, Field, validator, ConfigDict

from src.schemas.cafe import CafeShort
from src.schemas.mixins import TimeValidatorsMixin


def validate_date_not_past(v: Union[date_type, None]) -> Union[date_type,
                                                               None]:
    """Проверяет, что дата не в прошлом"""
    if v is not None and v < date_type.today():
        raise ValueError('Нельзя создавать слот в прошлом')
    return v


class TimeSlotBase(BaseModel, TimeValidatorsMixin):
    date: date_type = Field(..., description='Дата слота')
    start_time: time = Field(..., description='Время начала')
    end_time: time = Field(..., description='Время окончания')
    description: Optional[str] = Field(None, description='Описание слота')
    active: bool = Field(..., description='Активен ли слот')

    model_config = ConfigDict(from_attributes=True)

    _validate_date = validator('date')(validate_date_not_past)


class TimeSlotCreate(TimeSlotBase):
    cafe_id: int = Field(..., gt=0, description='ID кафе')


class TimeSlotUpdate(BaseModel, TimeValidatorsMixin):
    date: Optional[date_type] = Field(None, description='Дата слота')
    start_time: Optional[time] = Field(None, description='Время начала')
    end_time: Optional[time] = Field(None, description='Время окончания')
    description: Optional[str] = Field(None, description='Описание слота')
    active: Optional[bool] = Field(None, description='Активен ли слот')

    model_config = ConfigDict(from_attributes=True)

    _validate_date = validator('date')(validate_date_not_past)


class TimeSlotRead(TimeSlotBase):
    id: int
    cafe: CafeShort
    created_at: datetime
    updated_at: datetime


class TimeSlotShort(BaseModel):
    id: int
    cafe: CafeShort
    start_time: time
    end_time: time
    active: bool

    model_config = ConfigDict(from_attributes=True)
