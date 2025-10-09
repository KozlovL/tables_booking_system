from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DuplicateError
from src.core.logger import logger
from src.core.security import get_password_hash
from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate


class CRUDUser(CRUDBase):
    """CRUD из CRUDBase.

    Но create делает:
    - нормализацию username/phone/email/tg_id
    - проверку уникальности:
      (username, phone — всегда; email/tg_id — если заданы)
    - хэширование пароля -> hashed_password
    - единые дефолты для active/is_superuser.
    """

    model: type[User]

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        *,
        exclude_fields: set[str] | None = None,
        **extra_fields: Any,
    ) -> User:
        """Создаёт пользователя."""
        username = obj_in.username.strip()
        phone = obj_in.phone.strip()
        email = obj_in.email.lower().strip() if obj_in.email else None
        tg_id = obj_in.tg_id.strip() if obj_in.tg_id else None

        # 2) проверки уникальности
        request = select(User).where(
            or_(
                User.username == username,
                User.phone == phone,
                User.email == email if email else False,
                User.tg_id == tg_id if tg_id else False,
            ),
        )
        existing_user = (await session.execute(request)).scalar_one_or_none()
        if existing_user:
            if existing_user.username == username:
                raise DuplicateError(f"Пользователь с именем '{username}' ")

            if existing_user.phone == phone:
                raise DuplicateError(f"Пользователь с телефоном '{phone}' ")

            if email and existing_user.email == email:
                raise DuplicateError(f"Пользователь с email '{email}' ")

            if tg_id and existing_user.tg_id == tg_id:
                raise DuplicateError(f"Пользователь с Telegram ID '{tg_id}' ")

        data = {
            'username': username,
            'phone': phone,
            'email': email,
            'tg_id': tg_id,
            'hashed_password': get_password_hash(obj_in.password),
            'active': True,
            'is_superuser': False,
            'is_verified': False,
        }
        if extra_fields:
            data.update(extra_fields)

        db_obj = self.model(**data)
        session.add(db_obj)
        await session.flush()
        logger.info(
            'Создан пользователь: '
            f'{username}/{phone}/{email}/{tg_id} id={db_obj.id}',
        )
        return db_obj

    async def get_by_fields(
        self,
        session: AsyncSession,
        **fields: Any,
    ) -> Optional[User]:
        """Возвращает пользователя по полям или None."""
        conditions = []
        if fields.get('username'):
            conditions.append(User.username == fields['username'])
        if fields.get('phone'):
            conditions.append(User.phone == fields['phone'])
        if fields.get('email'):
            conditions.append(User.email == fields['email'])
        if fields.get('tg_id'):
            conditions.append(User.tg_id == fields['tg_id'])

        if not conditions:
            return None

        res = await session.execute(select(User).where(or_(*conditions)))
        return res.scalar_one_or_none()

    async def get_multi_filtered(
        self,
        session: AsyncSession,
        *,
        only_active: bool = True,
    ) -> list[User]:
        """Возвращает всех пользователей, можно фильтровать только активные."""
        stmt = select(self.model)
        if only_active:
            stmt = stmt.where(User.active.is_(True))
        res = await session.execute(stmt)
        users = list(res.scalars())
        logger.info(f'Получено {len(users)} кафе (only_active={only_active})')
        return users


user_crud = CRUDUser(User)
