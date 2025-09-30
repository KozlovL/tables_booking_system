from datetime import date, time
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.slot import TimeSlot


class CRUDTimeSlot(CRUDBase):
    async def check_time_conflict(
        self,
        cafe_id: int,
        slot_date: date,
        start_time: time,
        end_time: time,
        session: AsyncSession,
        exclude_slot_id: int | None = None,
    ) -> bool:
        """Проверка, пересекается ли слот с другими."""
        stmt = select(TimeSlot).where(
            and_(
                TimeSlot.cafe_id == cafe_id,
                TimeSlot.date == slot_date,
                TimeSlot.start_time < end_time,
                TimeSlot.end_time > start_time,
            )
        )
        if exclude_slot_id:
            stmt = stmt.where(TimeSlot.id != exclude_slot_id)

        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_multi_by_cafe_and_date(
        self,
        cafe_id: int,
        slot_date: date,
        session: AsyncSession,
        include_inactive: bool = False,
    ) -> list[TimeSlot]:
        stmt = select(TimeSlot).where(
            and_(
                TimeSlot.cafe_id == cafe_id,
                TimeSlot.date == slot_date,
            )
        )
        if not include_inactive:
            stmt = stmt.where(TimeSlot.active.is_(True))

        result = await session.execute(stmt)
        return list(result.scalars())

    async def get_with_cafe(
        self,
        slot_id: int,
        session: AsyncSession,
    ) -> TimeSlot | None:
        stmt = select(TimeSlot).where(TimeSlot.id == slot_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


time_slot_crud = CRUDTimeSlot(TimeSlot)
