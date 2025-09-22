from datetime import datetime
from pydantic import BaseModel, Field
from .cafe import CafeShort


class TableBase(BaseModel):
    seats_number: int = Field(..., description='Количество мест')
    description: str | None = Field(None, description='Описание столика')


class TableCreate(TableBase):
    pass


class TableUpdate(TableBase):
    seats_number: int | None = Field(None, description='Количество мест')
    description: str | None = Field(None, description='Описание столика')
    active: bool | None = Field(None, description='Объект активен?')


class TableShort(TableBase):
    id: int = Field(..., description='ID записи')
    cafe: CafeShort = Field(..., description='Кафе')
    active: bool = Field(..., description='Объект активен?')

    class Config:
        from_attributes = True


class Table(TableShort):
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    class Config:
        from_attributes = True
