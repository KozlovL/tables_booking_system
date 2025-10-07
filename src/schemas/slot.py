from datetime import date as date_type, datetime, time
from typing import Optional
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator
)

from src.schemas.cafe import CafeShort


class TimeSlotInputBase(BaseModel):
    """Базовая схема для ввода слотов"""
    date: Optional[date_type] = Field(None, description='Дата слота')
    start_time: Optional[time] = Field(None, description='Время начала')
    end_time: Optional[time] = Field(None, description='Время окончания')
    description: Optional[str] = Field(None, description='Описание слота')
    active: Optional[bool] = Field(None, description='Активен ли слот')

    model_config = ConfigDict(from_attributes=True)

    @field_validator('start_time', 'end_time', mode='before')
    @classmethod
    def normalize_time(cls, v):
        if v is None:
            return v
        if isinstance(v, time):
            return v.replace(second=0, microsecond=0, tzinfo=None)
        if isinstance(v, str):
            t = time.fromisoformat(v)
            return t.replace(second=0, microsecond=0, tzinfo=None)
        raise ValueError('Время должно быть в формате HH:MM')

    @model_validator(mode='after')
    def validate_times(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError(
                    'Время окончания должно быть позже времени начала'
                )
        return self


class TimeSlotCreate(TimeSlotInputBase):
    """Схема создания слота."""
    date: date_type = Field(..., description='Дата слота')
    start_time: time = Field(..., description='Время начала')
    end_time: time = Field(..., description='Время окончания')
    description: Optional[str] = Field(None, description='Описание слота')
    active: bool = Field(..., description='Активен ли слот')

    @model_validator(mode='after')
    def validate_not_in_past(self):
        now = datetime.now()
        slot_dt = datetime.combine(self.date, self.start_time)
        if slot_dt < now:
            raise ValueError('Нельзя создавать слот в прошлом')
        return self


class TimeSlotUpdate(TimeSlotInputBase):
    """Схема обновления слота."""


class TimeSlotShort(BaseModel):
    """Короткая схема слотов для связи."""
    id: int
    cafe: CafeShort
    date: date_type = Field(..., description='Дата слота')
    start_time: time = Field(..., description='Время начала')
    end_time: time = Field(..., description='Время окончания')
    description: Optional[str] = Field(None, description='Описание слота')
    active: bool = Field(..., description='Активен ли слот')

    model_config = ConfigDict(from_attributes=True)


class TimeSlotRead(TimeSlotShort):
    """Схема для чтения слотов."""
    created_at: datetime
    updated_at: datetime
