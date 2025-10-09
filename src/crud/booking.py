from datetime import date
from typing import Any, List, Optional

from sqlalchemy import Table, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models.booking import (
    BookingModel,
    BookingStatus,
    booking_dishes_table,
    booking_slots_table,
    booking_tables_table,
)
from src.models.slot import TimeSlot
from src.models.table import TableModel


class CRUDBooking(CRUDBase):
    """CRUD операции для бронирований."""

    def __init__(self) -> None:
        """Инициализатор CRUDBooking."""
        super().__init__(BookingModel)

    async def get_with_relations(
        self,
        booking_id: int,
        session: AsyncSession,
    ) -> BookingModel | None:
        """Получает бронирование со всеми связями."""
        stmt = (
            select(BookingModel)
            .options(
                selectinload(BookingModel.slots),
                selectinload(BookingModel.tables),
                selectinload(BookingModel.menu),
                selectinload(BookingModel.user),
                selectinload(BookingModel.cafe),
            )
            .where(BookingModel.id == booking_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        obj_in: Any,
        session: AsyncSession,
        *,
        exclude_fields: set[str] | None = None,
        **extra_fields: Any,
    ) -> BookingModel:
        """Создает бронирование с таблицами, слотами и меню."""
        tables_ids = obj_in.pop('tables', [])
        slots_ids = obj_in.pop('slots', [])
        menu_ids = obj_in.pop('menu', [])

        booking = await super().create(obj_in, session,
                                       exclude_fields=exclude_fields,
                                       **extra_fields)

        await self._add_booking_relations(session, booking.id,
                                          tables_ids,
                                          slots_ids, menu_ids)

        return await self.get_with_relations(booking.id, session)

    async def _add_booking_relations(
        self,
        session: AsyncSession,
        booking_id: int,
        tables_ids: List[int],
        slots_ids: List[int],
        menu_ids: List[int],
    ) -> None:
        """Добавляет связи бронирования с таблицами, слотами и блюдами."""
        for table_id in tables_ids:
            stmt = booking_tables_table.insert().values(booking_id=booking_id,
                                                        table_id=table_id)
            await session.execute(stmt)

        for slot_id in slots_ids:
            stmt = booking_slots_table.insert().values(booking_id=booking_id,
                                                       slot_id=slot_id)
            await session.execute(stmt)

        for dish_id in menu_ids:
            stmt = booking_dishes_table.insert().values(booking_id=booking_id,
                                                        dish_id=dish_id)
            await session.execute(stmt)

        await session.commit()

    async def update(
        self,
        db_obj: BookingModel,
        obj_in: Any,
        session: AsyncSession,
        *,
        exclude_fields: set[str] | None = None,
    ) -> BookingModel:
        """Обновляет бронирование и его связи."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field not in ['tables', 'slots', 'menu']:
                setattr(db_obj, field, value)

        if 'tables' in update_data:
            await self._update_booking_relations(
                session, db_obj.id,
                booking_tables_table, 'table_id',
                update_data['tables'],
            )

        if 'slots' in update_data:
            await self._update_booking_relations(
                session, db_obj.id,
                booking_slots_table, 'slot_id',
                update_data['slots'],
            )

        if 'menu' in update_data:
            await self._update_booking_relations(
                session, db_obj.id,
                booking_dishes_table, 'dish_id',
                update_data['menu'],
            )

        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def _update_booking_relations(
        self,
        session: AsyncSession,
        booking_id: int,
        relation_table: Table,
        id_column: str,
        new_ids: List[int],
    ) -> None:
        """Обновляет связи бронирования."""
        delete_stmt = relation_table.delete().where(
            relation_table.c.booking_id == booking_id,
        )
        await session.execute(delete_stmt)
        for item_id in new_ids:
            insert_stmt = relation_table.insert().values(
                booking_id=booking_id,
                **{id_column: item_id},
            )
            await session.execute(insert_stmt)

    async def get_user_bookings(
        self,
        session: AsyncSession,
        user_id: int,
        active_only: bool = True,
    ) -> List[BookingModel]:
        """Получает бронирования пользователя."""
        stmt = select(BookingModel).where(BookingModel.user_id == user_id)
        if active_only:
            stmt = stmt.where(BookingModel.active)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def check_booking_conflicts(
        self,
        session: AsyncSession,
        cafe_id: int,
        table_ids: List[int],
        slot_ids: List[int],
        booking_date: date,
        exclude_booking_id: Optional[int] = None,
    ) -> bool:
        """Проверяет конфликты бронирований для столов и слотов."""
        stmt = (
            select(BookingModel)
            .join(BookingModel.slots)
            .join(BookingModel.tables)
            .where(
                BookingModel.cafe_id == cafe_id,
                TimeSlot.date == booking_date,
                BookingModel.active.is_(True),
                BookingModel.status.in_(
                    [BookingStatus.BOOKED, BookingStatus.ACTIVE],
                ),
                TableModel.id.in_(table_ids),
                TimeSlot.id.in_(slot_ids),
            )
        )

        if exclude_booking_id:
            stmt = stmt.where(BookingModel.id != exclude_booking_id)

        result = await session.execute(stmt)
        existing_bookings = result.scalars().all()
        return len(existing_bookings) > 0

    async def update_status(
        self,
        session: AsyncSession,
        booking_id: int,
        status: BookingStatus,
    ) -> Optional[BookingModel]:
        """Обновляет статус бронирования."""
        booking = await self.get(booking_id, session)
        if booking:
            booking.status = status
            await session.commit()
            await session.refresh(booking)
        return booking


booking_crud = CRUDBooking()
