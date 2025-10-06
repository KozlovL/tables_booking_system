from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from .cafe import CafeShort


class TableBase(BaseModel):
    """Базовая схема для стола."""

    seats_number: PositiveInt = Field(..., description='Количество мест')
    description: str | None = Field(None, description='Описание столика')


class TableCreate(TableBase):
    """Схема создания стола."""

    pass


class TableUpdate(BaseModel):
    """Схема обновления стола."""

    seats_number: PositiveInt | None = Field(
        None,
        description='Количество мест',
    )
    description: str | None = Field(None, description='Описание столика')
    active: bool | None = Field(None, description='Объект активен?')


class TableShort(TableBase):
    """Краткая схема стола для выдачи наружу."""

    id: PositiveInt = Field(..., description='ID записи')
    cafe: CafeShort = Field(..., description='Кафе')
    active: bool = Field(..., description='Объект активен?')

    model_config = ConfigDict(from_attributes=True)


class Table(TableShort):
    """Схема стола с датами создания и обновления."""

    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    model_config = ConfigDict(from_attributes=True)
