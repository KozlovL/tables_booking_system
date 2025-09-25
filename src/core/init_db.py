# src/services/users.py
import logging

from src.core.config import settings

from src.core.db import AsyncSessionLocal
from src.core.security import get_password_hash
from src.crud.user import user_crud
from src.models.user import User

logger = logging.getLogger(__name__)


async def create_user(
    username: str,
    phone: str,
    password: str,
    *,
    email: str | None = None,
    tg_id: str | None = None,
    is_superuser: bool = False,
) -> User | None:
    """Создает пользователя в базе данных."""
    async with AsyncSessionLocal() as session:  # берём свою фабрику сессий
        # проверка — существует ли уже
        existing = await user_crud.get_by_fields(
            session,
            username=username,
            phone=phone,
            email=email,
            tg_id=tg_id,
        )
        if existing:
            logger.warning(f"Пользователь {username}/{phone}/{email} уже есть!")
            return None

        # создаём
        user = User(
            username=username.strip(),
            phone=phone.strip(),
            email=email.lower().strip() if email else None,
            tg_id=tg_id.strip() if tg_id else None,
            hashed_password=get_password_hash(password),
            active=True,
            is_superuser=is_superuser,
            is_verified=False,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

async def create_first_superuser() -> None:
    """Создает суперпользователя при старте приложения."""
    if settings.first_superuser_email and settings.first_superuser_password:
        user = await create_user(
            username=settings.first_superuser_username,
            phone=settings.first_superuser_phone,
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            is_superuser=True,
        )
        if user:
            logger.info("Создан суперпользователь")
        else:
            logger.info("Суперпользователь уже существует")
