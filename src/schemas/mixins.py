from pydantic import validator, model_validator
from src.api.validators import _to_naive_time


class TimeValidatorsMixin:
    """Миксин с валидаторами времени для схем"""

    @validator('start_time', 'end_time', pre=True)
    def parse_time(cls, v):
        if v is None:
            return None
        t = _to_naive_time(v)
        if t is None:
            raise ValueError('Неверный формат времени')
        return t

    @model_validator(mode='after')
    def check_time_order(cls, values):
        """Проверяет, что время окончания позже времени начала"""
        if hasattr(values, 'start_time') and hasattr(values, 'end_time'):
            start = values.start_time
            end = values.end_time
            if start and end and start >= end:
                raise ValueError(
                    'Время окончания должно быть позже времени начала')
        return values