from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.action import Action
from src.models.cafe import Cafe
from src.schemas.action import ActionCreate, ActionUpdate


class ActionCRUD:
    """CRUD операции для работы с акциями."""

    def _build_query(
            self,
            cafe_id: Optional[int] = None,
            cafe_ids: Optional[List[int]] = None,
            include_inactive: bool = False,
    ) -> select:
        """Базовый запрос для получения акций."""
        query = select(Action).options(
            selectinload(Action.cafe),
        )

        if cafe_id is not None:
            query = query.where(Action.cafe_id == cafe_id)
        elif cafe_ids is not None:
            query = query.where(Action.cafe_id.in_(cafe_ids))

        if not include_inactive:
            query = query.join(Cafe, Action.cafe_id == Cafe.id).where(
                Action.active.is_(True),
                Cafe.active.is_(True),
            )

        return query

    async def get_by_id(
            self,
            session: AsyncSession,
            action_id: int,
            include_inactive: bool = False,
    ) -> Optional[Action]:
        """Получение акции по ID."""
        query = select(Action).options(
            selectinload(Action.cafe).selectinload(Cafe.managers),
        ).where(Action.id == action_id)

        result = await session.execute(query)
        return result.scalars().first()

    async def get_multi(
            self,
            session: AsyncSession,
            cafe_id: Optional[int] = None,
            cafe_ids: Optional[List[int]] = None,
            include_inactive: bool = False,
    ) -> List[Action]:
        """Получение списка акций."""
        query = self._build_query(
            cafe_id=cafe_id,
            cafe_ids=cafe_ids,
            include_inactive=include_inactive,
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
            self,
            session: AsyncSession,
            obj_in: ActionCreate,
    ) -> Action:
        """Создание новой акции."""
        db_obj = Action(**obj_in.model_dump())
        session.add(db_obj)
        await session.commit()

        result = await session.execute(
            select(Action)
            .options(selectinload(Action.cafe))
            .where(Action.id == db_obj.id),
        )
        return result.scalar_one()

    async def update(
            self,
            session: AsyncSession,
            db_obj: Action,
            obj_in: ActionUpdate,
    ) -> Action:
        """Обновление акции."""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()

        result = await session.execute(
            select(Action)
            .options(selectinload(Action.cafe))
            .where(Action.id == db_obj.id),
        )
        return result.scalar_one()


action_crud = ActionCRUD()
