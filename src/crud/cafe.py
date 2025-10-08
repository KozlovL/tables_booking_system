from http.client import HTTPException
from typing import Optional

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes, selectinload

from src.core.exceptions import ResourceNotFoundError
from src.core.logger import logger
from src.crud.base import CRUDBase
from src.models.cafe import Cafe
from src.models.user import User
from src.schemas.cafe import CafeCreate, CafeUpdate

class CRUDCafe(CRUDBase):
    """CRUD для работы с моделью Cafe."""

    async def get_multi_filtered(
        self,
        session: AsyncSession,
        *,
        only_active: bool = True,
    ) -> list[Cafe]:
        """Возвращает все кафе, можно фильтровать только активные."""
        stmt = select(self.model).options(selectinload(Cafe.managers))
        if only_active:
            stmt = stmt.where(Cafe.active.is_(True))
        res = await session.execute(stmt)
        cafes = list(res.scalars())
        logger.info(f'Получено {len(cafes)} кафе (only_active={only_active})')
        return cafes

    async def create_with_managers(
        self,
        payload: CafeCreate,
        session: AsyncSession,
        *,
        photo_url: Optional[str] = None,
    ) -> Cafe:
        """ Создает кафе с менеджерами """
        # 1) создаём кафе через базовый CRUD, исключив поля отношений/фото

        cafe = await self.create(
            payload,
            session,
            exclude_fields={'photo', 'managers'},
            photo=photo_url,
        )

        managers: list[User] = []
        if payload.managers:
            res = await session.execute(
                select(User).where(User.id.in_(payload.managers)),
            )
            managers = list(res.scalars())
            found_ids = {u.id for u in managers}
            missing = [mid for mid in payload.managers if mid not in found_ids]
            if missing:
                raise ResourceNotFoundError(f"Нет таких менеджеров{missing}")

            attributes.set_committed_value(cafe, 'managers', [])
            cafe.managers.extend(managers)

        await session.flush()
        await session.commit()

        res = await session.execute(
            select(Cafe)
            .options(selectinload(Cafe.managers))
            .where(Cafe.id == cafe.id),
        )
        result = res.scalar_one()
        logger.info(
            f'Создано кафе id={result.id} с менеджерами {payload.managers}',
        )
        return result

    async def update_with_managers(
        self,
        cafe: Cafe,
        payload: CafeUpdate,
        session: AsyncSession,
        *,
        photo_url: Optional[str] = None,
    ) -> Cafe:
        """Обновляет скалярные поля (через CRUDBase.update) и,
        если присланы managers, валидирует список ID
        и заменяет связь many-to-many.
        """
        data = payload

        # Фото приходит base64 -> уже сохранено снаружи -> подменяем полем photo
        if "photo" in data:

            # в endpoint ты решаешь: сохранить/очистить фото; сюда передаёшь photo_url/None
            data["photo"] = photo_url

        # Обновляем только скалярные поля модели
        updatable =  {"name", "address", "phone", "description", "photo", "active"}
        await self.update(cafe, data, session, updatable_fields=updatable)

        if payload.managers is not None:
            ids = set(payload.managers) or []
            current_ids = {user.id for user in cafe.managers}
            # managers: list[User] = []

            # если переданы те же менеджеры
            if ids == current_ids:
                managers = cafe.managers
                pass

            else:
                res = await session.execute(select(User).where(User.id.in_(ids)))
                managers = list(res.scalars())
                found_ids = {u.id for u in managers}
                missing = [mid for mid in ids if mid not in found_ids]
                if missing:
                    raise ResourceNotFoundError(f"не найдены менедженры {missing}")

            cafe.managers = managers

        await session.flush()
        await session.commit()

        res = await session.execute(
            select(Cafe)
            .options(selectinload(Cafe.managers))
            .where(Cafe.id == cafe.id),
        )
        result = res.scalar_one()
        logger.info(
            f'Обновлено кафе id={result.id} с менеджерами {payload.managers}',
        )
        return result

    async def get_with_managers(
          self,
          cafe_id: int,
          session: AsyncSession
    ) -> Cafe | None:
        """
        Получает объект кафе по ID, подгружая
        связанную коллекцию менеджеров.
        """
        query = (
            select(self.model)
            .options(selectinload(self.model.managers))
            .where(self.model.id == cafe_id)
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()



cafe_crud = CRUDCafe(Cafe)