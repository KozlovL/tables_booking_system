from datetime import date as date_type, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TimeSlotBase(BaseModel):
    cafe_id: int = Field(..., gt=0, description='ID кафе')
    date: date_type = Field(..., description='Дата слота')
    start_time: time = Field(..., description='Время начала слота')
    end_time: time = Field(..., description='Время окончания слота')


class TimeSlotCreate(TimeSlotBase):
    pass


class TimeSlotUpdate(BaseModel):
    date: Optional[date_type] = Field(None, description='Дата слота')
    start_time: Optional[time] = Field(None, description='Время начала слота')
    end_time: Optional[time] = Field(None, description='Время окончания слота')
    active: Optional[bool] = Field(None, description='Активен ли слот')


class TimeSlotRead(TimeSlotBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
