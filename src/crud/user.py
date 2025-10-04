# src/crud/user.py
from __future__ import annotations
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.core.exceptions import InvalidUserData, UserAlreadyExists


class CRUDUser(CRUDBase):
    """CRUD из CRUDBase, но create делает:
    - нормализацию username/phone/email/tg_id
    - проверку уникальности (username, phone — всегда; email/tg_id — если заданы)
    - хэширование пароля -> hashed_password
    - единые дефолты для active/is_superuser
    """

    model: type[User]

    async def create(
        self,
        obj_in: UserCreate,
        session: AsyncSession,
        *,
        exclude_fields: set[str] | None = None,
        **extra_fields,
    ) -> User:
        # 1) нормализация входных полей
        username = obj_in.username.strip()
        phone = obj_in.phone.strip()
        email = obj_in.email.lower().strip() if getattr(obj_in, "email", None) else None
        tg_id = obj_in.tg_id.strip() if getattr(obj_in, "tg_id", None) else None

        if not username:
            raise InvalidUserData("Имя пользователя не может быть пустым")
        if not phone:
            raise InvalidUserData("Телефон не может быть пустым")

        # 2) проверки уникальности
        request = select(User).where(
            or_(
                User.username == username,
                User.phone == phone,
                User.email == email if email else False,
                User.tg_id == tg_id if tg_id else False,
            )
        )
        existing_user = (await session.execute(request)).scalar_one_or_none()
        if existing_user:
            if existing_user.username == username:
                raise UserAlreadyExists(f"Пользователь "
                                        f"с именем '{username}' "
                                        f"уже существует.")
            if existing_user.phone == phone:
                raise UserAlreadyExists(f"Пользователь "
                                        f"с телефоном '{phone}' "
                                        f"уже существует.")
            if email and existing_user.email == email:
                raise UserAlreadyExists(f"Пользователь "
                                        f"с email '{email}' "
                                        f"уже существует.")
            if tg_id and existing_user.tg_id == tg_id:
                raise UserAlreadyExists(f"Пользователь "
                                        f"с Telegram ID '{tg_id}' "
                                        f"уже существует.")

        # 3) собираем данные для модели
        data = {
            "username": username,
            "phone": phone,
            "email": email,
            "tg_id": tg_id,
            "hashed_password": get_password_hash(obj_in.password),
            "active": True,          # единая логика — активен по умолчанию
            "is_superuser": False,
            "is_verified": False,
        }
        if extra_fields:
            data.update(extra_fields)

        # 4) создаём объект как в базовом CRUD (но без пароля в явном виде)
        db_obj = self.model(**data)
        session.add(db_obj)
        await session.flush()  # получим id
        return db_obj

    async def get_by_fields(self, session, **fields):
        conditions = []
        if fields.get("username"):
            conditions.append(User.username == fields["username"])
        if fields.get("phone"):
            conditions.append(User.phone == fields["phone"])
        if fields.get("email"):
            conditions.append(User.email == fields["email"])
        if fields.get("tg_id"):
            conditions.append(User.tg_id == fields["tg_id"])

        if not conditions:
            return None

        res = await session.execute(select(User).where(or_(*conditions)))
        return res.scalar_one_or_none()


user_crud = CRUDUser(User)
