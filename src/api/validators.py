from fastapi import HTTPException, status
from sqlalchemy import exists, select
from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.cafe import cafe_crud
from src.crud.dish import dish_crud
from src.crud.table import table_crud
from src.models import Dish
from src.models.table import TableModel
from src.models.cafe import Cafe


async def get_table_or_404(
    session: AsyncSession,
    table_id: int,
    cafe_id: int,
    include_inactive: bool
) -> TableModel:
    """Проверка существования объекта с cafe_id, table_id"""

    table = await table_crud.get_by_id_and_cafe(
        session, table_id, cafe_id, include_inactive
    )
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол или кафе не найдены'
            )
    return table


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    """Функция проверки существования кафе"""
    exists_query = select(exists().where(Cafe.id == cafe_id))
    if not await session.scalar(exists_query):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено'
        )


async def check_dish_name_duplicate(
        dish_name: str,
        cafe: Cafe,
        session: AsyncSession,
) -> None:
    """Проверяет дублирование названия блюда в кафе."""
    dish = await dish_crud.get_by_field(
        session,
        name=dish_name,
        cafe=cafe,
    )
    if dish is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Блюдо с таким названием уже существует!',
        )


async def get_dish_or_404(
        dish_id: int,
        session: AsyncSession,
        extra_uploading: bool = False,
) -> Dish:
    dish = await dish_crud.get_by_field(
        session=session,
        extra_uploading=extra_uploading,
        id=dish_id,
    )
    if dish is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Блюдо не найдено'
        )
    return dish


async def get_cafe_or_404(
        cafe_id: int,
        session: AsyncSession,
) -> Cafe:
    """Функция получения кафе или ошибки 404."""
    cafe = await cafe_crud.get_by_field(
        session,
        id=cafe_id,
    )
    if cafe is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Кафе не найдено'
        )
    return cafe


async def check_unique_fields(  # проверяет уникальность полей(что бы избежать ошибки 500)
    session: AsyncSession,
    model,
    exclude_id: int | None,
    **field_values,
) -> None:
    """
    Проверяет, что указанные значения полей уникальны для модели,
    за исключением записи с exclude_id (если указан).
    """
    for field_name, value in field_values.items():
        if value is None:
            continue

        query = select(model).where(getattr(model, field_name) == value)
        if exclude_id is not None:
            query = query.where(model.id != exclude_id)

        existing = await session.scalar(query)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'{field_name} занято'
            )
