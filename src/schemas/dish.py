from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from src.core.logger import logger
from src.schemas.cafe import CafeShort


class DishCreate(BaseModel):
    """Схема создания блюда."""

    cafe_id: int
    name: str = Field(..., min_length=2, max_length=64)
    description: str
    price: PositiveInt
    photo: str | None = None

    @field_validator('photo', mode='before')
    def validate_photo(cls, photo: str | None) -> str | None:  # noqa: N805
        """Валидирует фото: не пустая строка."""
        try:
            if isinstance(photo, str) and len(photo) == 0:
                raise ValueError('Фото не может быть пустой строкой')
            logger.debug(f'Фото валидировано: {photo}')
            return photo
        except Exception as error:
            logger.error(
                'Ошибка валидации фото',
                details={'error': str(error)},
            )
            raise

    model_config = ConfigDict(extra='forbid')


class Dish(DishCreate):
    """Схема блюда для чтения."""

    id: int
    cafe: CafeShort
    active: bool
    created_at: datetime
    updated_at: datetime

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
    def validate_name(cls, name: str | None) -> str | None:  # noqa: N805
        """Валидирует название: не пустое и длина >= 2."""
        try:
            if name is None:
                raise ValueError('Название не может быть пустым')
            if isinstance(name, str) and len(name) < 2:
                raise ValueError(
                    'Название должно иметь длину больше 1 символа',
                )
            logger.debug(f'Название валидировано: {name}')
            return name
        except Exception as error:
            logger.error(
                'Ошибка валидации названия',
                details={'error': str(error)},
            )
            raise

    @field_validator('description', mode='before')
    def validate_description(
        cls,  # noqa: N805
        description: str | None,
    ) -> str | None:
        """Валидирует описание: не пустое и длина >= 2."""
        try:
            if description is None:
                raise ValueError('Описание не может быть пустым')
            if isinstance(description, str) and len(description) < 2:
                raise ValueError(
                    'Описание должно иметь длину больше 1 символа',
                )
            logger.debug(f'Описание валидировано: {description[:30]}')
            return description
        except Exception as error:
            logger.error(
                'Ошибка валидации описания',
                details={'error': str(error)},
            )
            raise

    @field_validator('price', mode='before')
    def validate_price(
        cls,  # noqa: N805
        price: PositiveInt | None = None,
    ) -> PositiveInt | None:
        """Валидирует цену: не пустая."""
        try:
            if price is None:
                raise ValueError('Цена не может быть пустой')
            logger.debug(f'Цена валидирована: {price}')
            return price
        except Exception as error:
            logger.error(
                'Ошибка валидации цены',
                details={'error': str(error)},
            )
            raise

    @field_validator('cafe_id', mode='before')
    def validate_cafe_id(cls, cafe_id: int | None) -> int | None:  # noqa: N805
        """Валидирует ID кафе: не пустой."""
        try:
            if cafe_id is None:
                raise ValueError('ID кафе не может быть пустым')
            logger.debug(f'ID кафе валидирован: {cafe_id}')
            return cafe_id
        except Exception as error:
            logger.error(
                'Ошибка валидации ID кафе',
                details={'error': str(error)},
            )
            raise

    model_config = ConfigDict(extra='forbid')
