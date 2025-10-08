from datetime import date, time, datetime
from typing import Any, Union, Optional, Type
from sqlalchemy import exists, select, and_

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppException, DuplicateError, ResourceNotFoundError
from src.crud.cafe import cafe_crud
from src.crud.dish import dish_crud
from src.crud.table import table_crud
from src.models import Dish
from src.models.table import TableModel
from src.models.cafe import Cafe
from src.core.db import Base
from src.core.logger import logger
from src.crud import (
    action_crud,
    cafe_crud,
    dish_crud,
    table_crud,
    time_slot_crud,
)
from src.models import Action, Cafe, Dish, TableModel, TimeSlot
from src.schemas.cafe import CafeCreate


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
        raise ResourceNotFoundError(resource_name="Стол")
    return table


async def cafe_exists(cafe_id: int, session: AsyncSession) -> None:
    """Функция проверки существования кафе."""
    exists_query = select(exists().where(Cafe.id == cafe_id))
    if not await session.scalar(exists_query):
        logger.warning('Кафе не найдено', details={'cafe_id': cafe_id})
        raise ResourceNotFoundError(resource_name="Кафе")


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
        raise DuplicateError(
                entity='Блюдо'
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
        raise ResourceNotFoundError(resource_name="блюдо")
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
        raise ResourceNotFoundError(resource_name="Кафе")
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
            raise DuplicateError()


async def get_timeslot_or_404(
    timeslot_id: int,
    session: AsyncSession,
) -> TimeSlot:
    """Проверяет, что слот существует; если нет — 404."""
    timeslot = await time_slot_crud.get(obj_id=timeslot_id, session=session)
    if not timeslot:
        raise ResourceNotFoundError(resource_name='Слот')
    return timeslot


async def get_timeslot_or_404_with_relations(
    timeslot_id: int,
    cafe_id: int,
    session: AsyncSession,
) -> TimeSlot:
    """Проверяет, что слот существует; если нет — 404."""
    timeslot = await time_slot_crud.get_with_cafe(
        slot_id=timeslot_id,
        cafe_id=cafe_id,
        session=session,
    )
    if not timeslot:
        raise ResourceNotFoundError(resource_name='Слот')
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
        raise AppException(
            detail='Временной слот пересекается с существующим!'
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

    await check_timeslot_intersections(
        cafe_id=cafe_id,
        slot_date=slot_date,
        start_time=start_time,
        end_time=end_time,
        timeslot_id=exclude_slot_id,
        session=session,
    )


async def get_action_or_404(
    action_id: int,
    session: AsyncSession,
) -> Action:
    """Проверяет есть ли такая акция."""
    action = await action_crud.get_by_id(action_id=action_id, session=session)
    if not action:
        raise ResourceNotFoundError(resource_name='Акция')
    return action


async def check_cafe_name_duplicate(
    cafe: CafeCreate,
    session: AsyncSession,
    exclude_id: int | None = None,
) -> None:
    """Проверяет уникальность названия блюда в кафе."""
    stmt = select(Cafe.name).where(Cafe.name == cafe.name)

    if exclude_id is not None:
        stmt = stmt.where(Cafe.id != exclude_id)

    query = select(exists(stmt))

    result = await session.execute(query)
    if result.scalar():
        logger.warning(
                'Кафе с таким названием уже существует',
                details={'cafe_name': cafe.name},
        )
        raise DuplicateError(
                entity='Кафе с таким именем'
        )


async def cafe_exists_and_active(cafe_id: int, session: AsyncSession) -> None:
    """Функция проверки существования кафе."""
    exists_query = select(exists().where(
        and_(
            Cafe.id == cafe_id,
            Cafe.active.is_(True)
        )
    ))
    if not await session.scalar(exists_query):
        logger.warning('Кафе не найдено', details={'cafe_id': cafe_id})
        raise ResourceNotFoundError(
            resource_name='Кафе'
        )


async def validate_table_for_booking(
    table_ids: list[int],
    cafe_id: int,
    guests_number: int,
    session: AsyncSession,
) -> None:
    if not table_ids:
        raise AppException(detail='Список столов не может быть пустым')
    stmt = select(TableModel).where(
        and_(
            TableModel.id.in_(table_ids),
            TableModel.cafe_id == cafe_id,
            TableModel.active.is_(True)
        )
    )
    result = await session.execute(stmt)
    found_tables = result.scalars().all()
    found_ids = {table.id for table in found_tables}

    if len(found_ids) != len(table_ids):
        invalid = set(table_ids) - found_ids
        logger.warning(
            'Один или несколько столов не найдены или неактивны',
            details={'cafe_id': cafe_id, 'tables': list(invalid)}
        )
        raise ResourceNotFoundError(
            resource_name='Один или несколько столов'
        )

    total_seats = sum(table.seats_number for table in found_tables)
    if guests_number > total_seats:
        raise AppException(
            detail=f'Общая вместимость столов {total_seats} меньше '
                   f'числа гостей {guests_number}'
        )


async def validate_slot_for_booking(
    slot_ids: list[int],
    cafe_id: int,
    session: AsyncSession,
) -> date:
    if not slot_ids:
        raise AppException(
            detail='Список слотов не может быть пустым'
        )
    stmt = select(TimeSlot.id,  TimeSlot.date).where(
        and_(
            TimeSlot.id.in_(slot_ids),
            TimeSlot.cafe_id == cafe_id,
            TimeSlot.active.is_(True),
        )
    )
    result = await session.execute(stmt)
    slots = result.fetchall()

    found_ids = {slot.id for slot in slots}

    if len(slots) != len(slot_ids):
        invalid = set(slot_ids) - found_ids
        logger.warning(
            'Один или несколько слотов не найдены или неактивны',
            details={'cafe_id': cafe_id, 'invalid_slot_ids': list(invalid)}
        )
        raise ResourceNotFoundError(
            resource_name='Один или несколько слотов'
        )
    slot_dates = {slot.date for slot in slots}
    if len(slot_dates) != 1:
        logger.warning(
            'Все слоты должны быть на одну дату',
            details={'cafe_id': cafe_id, 'slot_dates': slot_dates}
        )
        raise AppException(
            detail='Все слоты должны быть на одну дату.',
        )
    return slot_dates.pop()


async def validate_dish_for_booking(
    dish_ids: list[int],
    cafe_id: int,
    session: AsyncSession,
) -> None:
    if not dish_ids:
        return
    unique_dish_ids = set(dish_ids)

    stmt = select(Dish.id).where(
        and_(
            Dish.id.in_(unique_dish_ids),
            Dish.cafe_id == cafe_id,
            Dish.active.is_(True),
        )
    )
    result = await session.execute(stmt)
    dishes = set(result.scalars().all())

    if len(dishes) != len(unique_dish_ids):
        invalid = set(unique_dish_ids) - dishes
        logger.warning(
            'Одно или несколько блюд не найдены или неактивны',
            details={'cafe_id': cafe_id, 'invalid_dish_ids': list(invalid)}
        )
        raise ResourceNotFoundError(
            resource_name='Одно или несколько блюд'
        )
