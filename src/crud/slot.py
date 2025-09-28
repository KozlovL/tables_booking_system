from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models.slot import TimeSlot


class CRUDTimeSlot(CRUDBase):
    async def get_with_cafe(self, slot_id: int, session: AsyncSession):
        """Получить слот с информацией о кафе."""
        stmt = (
            select(TimeSlot)
            .options(selectinload(TimeSlot.cafe))
            .where(TimeSlot.id == slot_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi_by_cafe_and_date(
        self,
        cafe_id: int,
        slot_date: date,
        session: AsyncSession,
        only_active: bool = True
    ):
        """Получить все слоты конкретного кафе на определенную дату."""
        stmt = select(TimeSlot).where(
            TimeSlot.cafe_id == cafe_id,
            TimeSlot.date == slot_date
        )
        if only_active:
            stmt = stmt.where(TimeSlot.active.is_(True))

        result = await session.execute(stmt)
        return list(result.scalars())

    async def get_multi_by_cafe(self, cafe_id: int,
                                session: AsyncSession,
                                only_active: bool = True):
        """Получить все слоты конкретного кафе."""
        stmt = select(TimeSlot).where(TimeSlot.cafe_id == cafe_id)
        if only_active:
            stmt = stmt.where(TimeSlot.active.is_(True))

        result = await session.execute(stmt)
        return list(result.scalars())

    async def check_time_conflict(
        self,
        cafe_id: int,
        slot_date: date,
        start_time: str,
        end_time: str,
        session: AsyncSession,
        exclude_slot_id: int = None
    ):
        """Проверить конфликт времени с существующими слотами на ту же дату."""
        stmt = select(TimeSlot).where(
            TimeSlot.cafe_id == cafe_id,
            TimeSlot.date == slot_date,
            TimeSlot.active.is_(True)
        )

        if exclude_slot_id:
            stmt = stmt.where(TimeSlot.id != exclude_slot_id)

        result = await session.execute(stmt)
        existing_slots = list(result.scalars())

        for slot in existing_slots:
            if not (end_time <= slot.start_time or
                    start_time >= slot.end_time):
                return True

        return False


time_slot_crud = CRUDTimeSlot(TimeSlot)
