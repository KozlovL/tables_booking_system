from http.client import HTTPException
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes, selectinload

from src.core.exceptions import ResourceNotFoundError
from src.crud.base import CRUDBase
from src.models.cafe import Cafe
from src.models.user import User

class CRUDCafe(CRUDBase):
    async def get_multi_filtered(
            self,
            session: AsyncSession,
            *,
            only_active: bool = True,
    ):
        stmt = (
            select(self.model)
            .options(selectinload(Cafe.managers))

        )
        if only_active:
            stmt = stmt.where(Cafe.active.is_(True))
        res = await session.execute(stmt)
        return list(res.scalars())

    async def create_with_managers(
            self,
            payload,  # CafeCreate
            session: AsyncSession,
            *,
            photo_url: Optional[str] = None,
    ) -> Cafe:
        """ создает кафе с менеджерами """
        # 1) создаём кафе через базовый CRUD, исключив поля отношений/фото

        cafe = await self.create(
            payload,
            session,
            exclude_fields={'photo', 'managers'},
            photo=photo_url,
        )

        # 2) подгружаем менеджеров по ID, если они есть
        managers = []
        if payload.managers:
            res = await session.execute(
                select(User).where(User.id.in_(payload.managers)),
            )
            managers = list(res.scalars())
            found_ids = {u.id for u in managers}
            missing = [mid for mid in payload.managers if mid not in found_ids]
            if missing:
                raise ResourceNotFoundError(f"Нет таких менеджеров{missing}")

            attributes.set_committed_value(cafe, "managers", [])  # коллекция «инициализирована»
            cafe.managers.extend(managers)

            cafe.managers = managers

        # 3) фиксируем и возвращаем с подзагрузкой менеджеров
        await session.flush()
        cafe_id = cafe.id
        await session.commit()

        res = await session.execute(
            select(Cafe)
            .options(selectinload(Cafe.managers))
            .where(Cafe.id == cafe_id),
        )
        return res.scalar_one()

    async def update_with_managers(
            self,
            cafe: Cafe,
            payload,  # CafeUpdate
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

        # Если managers присутствует в payload — заменить связь
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
        cafe_id = cafe.id
        await session.commit()

        # Возвращаем с подзагрузкой managers, чтобы не
        # ловить MissingGreenlet при сериализации
        res = await session.execute(
            select(Cafe)
            .options(selectinload(Cafe.managers))
            .where(Cafe.id == cafe_id),
        )
        return res.scalar_one()

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
