from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt

from .cafe import CafeShort


class TableBase(BaseModel):
    """Базовая модель стола с общими полями."""

    seats_number: PositiveInt = Field(..., description='Количество мест')
    description: str | None = Field(None, description='Описание столика')


class TableCreate(TableBase):
    """Модель для создания нового стола."""


class TableUpdate(BaseModel):
    """Модель для обновления существующего стола."""

    seats_number: PositiveInt | None = Field(
        None, description='Количество мест')
    description: str | None = Field(None, description='Описание столика')
    active: bool | None = Field(None, description='Объект активен?')


class TableShort(TableBase):
    """Краткая модель стола для использования в связанных сущностях."""

    id: PositiveInt = Field(..., description='ID записи')
    cafe: CafeShort = Field(..., description='Кафе')
    active: bool = Field(..., description='Объект активен?')

    model_config = ConfigDict(from_attributes=True)


class Table(TableShort):
    """Полная модель стола с временными метками создания и обновления."""

    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    model_config = ConfigDict(from_attributes=True)
