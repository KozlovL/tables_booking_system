from typing import Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Action, Cafe, User
from src.schemas.action import ActionCreate, ActionUpdate


class ActionCRUD:
    """CRUD операции для работы с акциями."""

    async def get_by_id(
            self,
            session: AsyncSession,
            action_id: int,
    ) -> Optional[Action]:
        """Получение акции по ID."""
        query = select(Action).options(
            selectinload(Action.cafe).selectinload(Cafe.managers),
        ).where(Action.id == action_id)

        result = await session.execute(query)
        return result.scalars().first()

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
            .options(selectinload(Action.cafe).selectinload(Cafe.managers))
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
        await session.refresh(db_obj)
        result = await session.execute(
            select(Action)
            .options(selectinload(Action.cafe).selectinload(Cafe.managers))
            .where(Action.id == db_obj.id),
        )
        return result.scalar_one()

    async def get_actions_with_access_control(
        self,
        session: AsyncSession,
        cafe: Cafe | None,
        active_only: bool,
        current_user: User,
    ) -> list[Action]:
        """Получаем список акций с фильтрацией доступа."""
        query = select(Action).options(
            selectinload(Action.cafe).selectinload(Cafe.managers),
        )

        if cafe is not None:
            query = query.where(Action.cafe_id == cafe.id)
        if active_only:
            query = query.where(
                Action.active.is_(True),
            )
        else:
            if current_user.is_superuser:
                pass
            elif current_user.managed_cafe_ids:
                query = query.where(
                    or_(
                        Action.active.is_(True),
                        and_(
                            Action.active.is_(False),
                            Action.cafe_id.in_(current_user.managed_cafe_ids),
                        ),
                    ),
                )

        result = await session.execute(query)
        return list(result.scalars().all())


action_crud = ActionCRUD()
