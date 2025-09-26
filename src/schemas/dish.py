from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.schemas.cafe import CafeShort


class DishCreate(BaseModel):
    """Схема создания блюда."""
    cafe: int
    name: str = Field(
        ...,
        min_length=2,
        max_length=64,
    )
    description: str
    price: int
    photo: Optional[str]

    # Выбрасываем ошибку при передаче лишних полей
    model_config = {
        'extra': 'forbid'
    }


class DishDB(DishCreate):
    """Схема блюда для чтения."""
    id: int
    cafe: CafeShort
    active: bool
    created_at: datetime
    updated_at: datetime

    # Чтобы схема могла принимать ORM-объекты
    class Config:
        orm_mode = True


class DishUpdate(DishCreate):
    """Схема обновления блюда."""
    cafe: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    photo: Optional[str] = None
    active: Optional[bool] = None

    @field_validator('name')
    def validate_name(cls, name: Optional[str]) -> Optional[str]:
        if name is not None and not name.strip():
            raise ValueError('Название не может быть пустым')
        return name

    @field_validator('description')
    def validate_description(cls, description: Optional[str]) -> Optional[str]:
        if description is not None and not description.strip():
            raise ValueError('Описание не может быть пустым')
        return description

    @field_validator('price')
    def validate_price(cls, price: Optional[int]) -> Optional[int]:
        if price is not None and price < 0:
            raise ValueError('Цена не может быть отрицательной')
        return price
