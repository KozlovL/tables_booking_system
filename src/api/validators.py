from datetime import date, time, datetime
from typing import Any, Union, Optional, Type
from fastapi import HTTPException, status
from sqlalchemy import exists, select
from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import Base
from src.core.logger import logger
from src.crud import cafe_crud, dish_crud, table_crud, time_slot_crud
from src.models import Cafe, Dish, TableModel, TimeSlot


async def get_table_or_404(
    session: AsyncSession,
    table_id: int,
    cafe_id: int,
    include_inactive: bool,
) -> TableModel:
    """Проверка существования объекта с cafe_id, table_id."""
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
    """Функция проверки существования кафе."""
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


# def _to_naive_time(value: Union[str, datetime, time, None]) -> time | None:
#     """Нормализует время для передачи в CRUD"""
#     if value is None:
#         return None

#     if isinstance(value, str):
#         if 'T' in value:
#             value = value.split('T', 1)[1]
#         if '+' in value:
#             value = value.split('+', 1)[0]
#         try:
#             return time.fromisoformat(value)
#         except Exception as exc:
#             raise HTTPException(
#                 status_code=400,
#                 detail='Неправильный формат времени'
#             ) from exc

#     if isinstance(value, datetime):
#         t = value.timetz() if value.tzinfo else value.time()
#         return t.replace(tzinfo=None) if t.tzinfo else t

#     if isinstance(value, time):
#         return value.replace(tzinfo=None) if value.tzinfo else value
#     return None


async def get_timeslot_or_404(
    timeslot_id: int,
    session: AsyncSession,
) -> TimeSlot:
    """Проверяет, что слот существует; если нет — 404."""
    timeslot = await time_slot_crud.get(obj_id=timeslot_id, session=session)
    if not timeslot:
        raise HTTPException(status_code=404, detail='Слот не найден!')
    return timeslot


async def get_timeslot_or_404_with_relations(
    timeslot_id: int,
    session: AsyncSession,
) -> TimeSlot:
    """Проверяет, что слот существует; если нет — 404."""
    timeslot = await time_slot_crud.get_with_cafe(
        slot_id=timeslot_id, session=session
    )
    if not timeslot:
        raise HTTPException(status_code=404, detail='Слот не найден!')
    return timeslot


async def check_timeslot_intersections(
    *,
    cafe_id: int,
    slot_date: date,
    start_time: time,
    end_time: time,
    timeslot_id: Optional[int] = None,
    session: AsyncSession,
) -> None:
    """Проверяет пересечения временных слотов"""
    if await time_slot_crud.check_time_conflict(
        cafe_id=cafe_id,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
        session=session,
        exclude_slot_id=timeslot_id,
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Временной слот пересекается с существующим!',
        )


async def validate_and_check_conflicts(
    *,
    cafe_id: int,
    slot_date: date,
    start_time: Union[str, time, datetime],
    end_time: Union[str, time, datetime],
    session: AsyncSession,
    exclude_slot_id: Optional[int] = None,
) -> None:
    """Проверка для create/update слотов"""
    start_time = start_time.replace(second=0, microsecond=0, tzinfo=None)
    end_time = end_time.replace(second=0, microsecond=0, tzinfo=None)
    slot_datetime = datetime.combine(slot_date, start_time)
    if start_time is None or end_time is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Неверный формат времени'
            )

    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Время начала должно быть раньше времени окончания',
        )

    if slot_datetime < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Нельзя создавать слот в прошлом',
        )

    await check_timeslot_intersections(
        cafe_id=cafe_id,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
        timeslot_id=exclude_slot_id,
        session=session,
    )


# async def get_slot_or_404(
#     slot_id: int,
#     session: AsyncSession,
#     include_inactive: bool
# ) -> TableModel:
#     """Проверка существования объекта с cafe_id, slot_id."""
#     slot = await time_slot_crud.get_with_cafe(
#         slot_id, session
#     )
#     if not slot:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Слот или кафе не найдены'
#             )
#     return slot
