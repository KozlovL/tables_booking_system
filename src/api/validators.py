from http import HTTPStatus
from typing import Any, Type

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base
from src.core.logger import logger
from src.crud.cafe import cafe_crud
from src.crud.dish import dish_crud
from src.crud.table import table_crud
from src.models import Dish
from src.models.cafe import Cafe
from src.models.table import TableModel


async def get_table_or_404(
    session: AsyncSession,
    table_id: int,
    cafe_id: int,
    include_inactive: bool,
) -> TableModel:
    """Проверяет наличие стола в кафе."""
    table = await table_crud.get_by_id_and_cafe(
        session,
        table_id,
        cafe_id,
        include_inactive,
    )
    if not table:
        logger.warning(
            'Стол или кафе не найдены',
            details={'table_id': table_id, 'cafe_id': cafe_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Стол или кафе не найдены',
        )
    return table


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    """Проверяет существование кафе."""
    exists_query = select(exists().where(Cafe.id == cafe_id))
    if not await session.scalar(exists_query):
        logger.warning('Кафе не найдено', details={'cafe_id': cafe_id})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Кафе не найдено',
        )


async def check_dish_name_duplicate(
    dish_name: str,
    cafe: Cafe,
    session: AsyncSession,
) -> None:
    """Проверяет уникальность названия блюда в кафе."""
    dish = await dish_crud.get_by_field(
        session,
        name=dish_name,
        cafe=cafe,
    )
    if dish is not None:
        logger.warning(
            'Блюдо с таким названием уже существует',
            details={'dish_name': dish_name, 'cafe_id': cafe.id},
        )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Блюдо с таким названием уже существует!',
        )


async def get_dish_or_404(
    dish_id: int,
    session: AsyncSession,
    extra_uploading: bool = False,
) -> Dish:
    """Возвращает блюдо или ошибку 404."""
    dish = await dish_crud.get_by_field(
        session=session,
        extra_uploading=extra_uploading,
        id=dish_id,
    )
    if dish is None:
        logger.warning('Блюдо не найдено', details={'dish_id': dish_id})
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Блюдо не найдено',
        )
    return dish


async def get_cafe_or_404(
    cafe_id: int,
    session: AsyncSession,
) -> Cafe:
    """Возвращает кафе или ошибку 404."""
    cafe = await cafe_crud.get_by_field(
        session,
        id=cafe_id,
    )
    if cafe is None:
        logger.warning('Кафе не найдено', details={'cafe_id': cafe_id})
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Кафе не найдено',
        )
    return cafe


async def check_unique_fields(
    session: AsyncSession,
    model: Type[Base],  # type: ignore
    exclude_id: int | None,
    **field_values: Any,
) -> None:
    """Проверяет уникальность указанных полей модели."""
    for field_name, value in field_values.items():
        if value is None:
            continue

        query = select(model).where(getattr(model, field_name) == value)
        if exclude_id is not None:
            query = query.where(model.id != exclude_id)

        existing = await session.scalar(query)
        if existing:
            logger.warning(
                f'{field_name} уже занято',
                details={
                    'field': field_name,
                    'value': value,
                    'exclude_id': exclude_id,
                },
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'{field_name} занято',
            )
