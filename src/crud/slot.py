from datetime import date, time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.models import BookingModel, BookingStatus, Cafe, TimeSlot
from src.schemas.slot import TimeSlotCreate, TimeSlotUpdate


class CRUDTimeSlot(CRUDBase):
    """CRUD операции для временных слотов."""

    async def _check_no_active_bookings(
            self, slot_id: int,
            session: AsyncSession,
    ) -> None:
        """Запрещает изменять слот если он booked или active."""
        stmt = (
            select(BookingModel.id)
            .join(BookingModel.slots)
            .where(
                TimeSlot.id == slot_id,
                BookingModel.active.is_(True),
                BookingModel.status.in_(
                    [BookingStatus.BOOKED, BookingStatus.ACTIVE],
                ),
            )
            .limit(1)
        )
        if await session.scalar(stmt) is not None:
            print('Замени меня на кастомный обработчик ошибок')

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
            TimeSlot.cafe_id == cafe_id,
            TimeSlot.date == slot_date,
            TimeSlot.start_time < end_time,
            TimeSlot.end_time > start_time,
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
        """Получает список слотов для кафе на указанную дату."""
        stmt = select(TimeSlot).options(
            selectinload(
                TimeSlot.cafe).selectinload(Cafe.managers)).where(
                TimeSlot.cafe_id == cafe_id,
                TimeSlot.date == slot_date,
        )
        if not include_inactive:
            stmt = stmt.where(TimeSlot.active.is_(True))

        result = await session.execute(stmt)
        return list(result.scalars())

    async def get_with_cafe(
        self,
        slot_id: int,
        cafe_id: int,
        session: AsyncSession,
    ) -> TimeSlot | None:
        """Получает слот по ID с проверкой принадлежности к кафе."""
        result = await session.execute(
            select(TimeSlot)
            .options(selectinload(TimeSlot.cafe).selectinload(Cafe.managers))
            .where(
                TimeSlot.id == slot_id,
                TimeSlot.cafe_id == cafe_id,
            ),
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        cafe_id: int,
        obj_in: TimeSlotCreate,
        session: AsyncSession,
    ) -> TimeSlot:
        """Создает новый временной слот для указанного кафе."""
        db_obj = TimeSlot(**obj_in.model_dump(), cafe_id=cafe_id)
        session.add(db_obj)
        await session.commit()
        result = await session.execute(
            select(TimeSlot)
            .options(selectinload(TimeSlot.cafe).selectinload(Cafe.managers))
            .where(TimeSlot.id == db_obj.id),
        )
        return result.scalar_one()

    async def update(
        self,
        db_obj: TimeSlot,
        obj_in: TimeSlotUpdate,
        session: AsyncSession,
    ) -> TimeSlot:
        """Обновляет слот.

        И возвращает обновлённый объект с загруженными связями.
        """
        await self._check_no_active_bookings(db_obj.id, session)
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        result = await session.execute(
            select(TimeSlot)
            .options(selectinload(TimeSlot.cafe).selectinload(Cafe.managers))
            .where(TimeSlot.id == db_obj.id),
        )

        return result.scalar_one()


time_slot_crud = CRUDTimeSlot(TimeSlot)
