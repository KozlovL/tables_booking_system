# src/crud/user.py
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import get_password_hash
from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate


class CRUDUser(CRUDBase):
    """CRUD из CRUDBase, но create делает:
    - нормализацию username/phone/email/tg_id
    - проверку уникальности (username, phone — всегда; email/tg_id — если заданы)
    - хэширование пароля -> hashed_password
    - единые дефолты для active/is_superuser/is_verified
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
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        if not phone:
            raise HTTPException(status_code=400, detail="Phone cannot be empty")

        # 2) проверки уникальности
        conditions = [User.username == username, User.phone == phone]
        if email:
            conditions.append(User.email == email)
        if tg_id:
            conditions.append(User.tg_id == tg_id)

        res = await session.execute(select(User.id).where(or_(*conditions)))
        if res.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with same username/phone/email/tg_id already exists",
            )

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
