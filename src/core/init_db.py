import contextlib
import logging

from fastapi_users.exceptions import UserAlreadyExists
from pydantic import EmailStr

from src.core.config import settings
from src.core.db import get_async_session
from src.core.user import get_user_db, get_user_manager
from src.schemas.user import UserCreate

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


logger = logging.getLogger(__name__)


async def create_user(
        email: EmailStr, password: str, is_superuser: bool = False,
) -> None:
    """Создает пользователя в базе данных."""
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    await user_manager.create(
                        UserCreate(
                            email=email,
                            password=password,
                            is_superuser=is_superuser,
                        ),
                    )
    except UserAlreadyExists:
        logger.warning(f"Пользователь с таким {email} уже есть!")


async def create_first_superuser() -> None:
    """Создает суперпользователя при старте приложения."""
    if (settings.first_superuser_email is not None and
            settings.first_superuser_password is not None):
        await create_user(
            email=settings.first_superuser_email,
            password=settings.first_superuser_password,
            is_superuser=True,
        )
