from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, PositiveInt, model_serializer

from src.schemas.cafe import CafeShort


# Базовые схемы
class ActionBase(BaseModel):
    """Базовая схема акции с общими полями."""

    description: str


class ActionCreate(ActionBase):
    """Схема для создания новой акции."""

    cafe_id: int


class ActionUpdate(ActionBase):
    """Схема для обновления существующей акции."""

    cafe_id: Optional[PositiveInt] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class ActionInDBBase(ActionBase):
    """Базовая схема акции для работы с базой данных."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cafe_id: int
    active: Optional[bool] = True
    created_at: datetime
    updated_at: datetime


class Action(ActionInDBBase):
    """Схема акции для возврата из API."""

    pass


class ActionWithCafe(BaseModel):
    """Схема с полной информацией о кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cafe: CafeShort
    description: str
    active: bool
    created_at: datetime
    updated_at: datetime

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """Сериализатор модели для преобразования данных в API-формат."""
        return {
            'id': self.id,
            'cafe': self.cafe,
            'description': self.description,
            'active': self.active,
            'created_at': self.created_at.isoformat(
                timespec='milliseconds') + 'Z',
            'updated_at': self.updated_at.isoformat(
                timespec='milliseconds') + 'Z',
        }
