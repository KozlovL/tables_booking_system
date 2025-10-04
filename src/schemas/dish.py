from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict, PositiveInt

from src.schemas.cafe import CafeShort


class DishCreate(BaseModel):
    """Схема создания блюда."""
    cafe_id: int
    name: str = Field(
        ...,
        min_length=2,
        max_length=64,
    )
    description: str
    price: PositiveInt
    photo: str | None = None

    @field_validator('photo', mode='before')
    def validate_photo(cls, photo: str | None) -> str | None:
        if isinstance(photo, str) and len(photo) == 0:
            raise ValueError('Фото не может быть пустой строкой')
        return photo

    # Выбрасываем ошибку при передаче лишних полей
    model_config = ConfigDict(extra='forbid')


class Dish(DishCreate):
    """Схема блюда для чтения."""
    id: int
    cafe: CafeShort
    active: bool
    created_at: datetime
    updated_at: datetime

    # Чтобы схема могла принимать ORM-объекты
    model_config = ConfigDict(from_attributes=True)


class DishUpdate(DishCreate):
    """Схема обновления блюда."""
    cafe_id: int | None = None
    name: str | None = None
    description: str | None = None
    price: PositiveInt | None = None
    photo: str | None = None
    active: bool | None = None

    @field_validator('name', mode='before')
    def validate_name(cls, name: str | None) -> str | None:
        if name is None:
            raise ValueError('Название не может быть пустым')
        if isinstance(name, str) and len(name) < 2:
            raise ValueError('Название должно иметь длину больше 1 символа')
        return name

    @field_validator('description', mode='before')
    def validate_description(cls, description: str | None) -> str | None:
        if description is None:
            raise ValueError('Описание не может быть пустым')
        if isinstance(description, str) and len(description) < 2:
            raise ValueError('Название должно иметь длину больше 1 символа')
        return description

    @field_validator('price', mode='before')
    def validate_price(
            cls,
            price: PositiveInt | None = None,
    ) -> PositiveInt | None:
        if price is None:
            raise ValueError('Цена не может быть пустой')
        return price

    @field_validator('cafe_id', mode='before')
    def validate_cafe_id(cls, cafe_id: int | None) -> int | None:
        if cafe_id is None:
            raise ValueError('ID кафе не может быть пустым')
        return cafe_id

    # Выбрасываем ошибку при передаче лишних полей
    model_config = ConfigDict(extra='forbid')
