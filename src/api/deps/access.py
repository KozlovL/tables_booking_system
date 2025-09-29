from http import HTTPStatus

from fastapi import Depends, Path, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists
from typing import Optional

from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.crud.cafe import cafe_crud
from src.models import User, cafe_managers_table, Cafe


async def _is_manager_or_admin(
    cafe_id: int | None,
    user: User,
    session: AsyncSession
) -> bool:
    """
    Базовая функция для определения администратора, менеджера или пользователя.
    Менеджер и администратор - True.
    Пользователь - False
    """
    if not user:
        return False
    if user.is_superuser:
        return True
    query = select(exists().where(
        cafe_managers_table.c.user_id == user.id,
        cafe_managers_table.c.cafe_id == cafe_id
    ))
    return await session.scalar(query)


async def get_include_inactive(
    cafe_id: int = Path(...),
    current_user: Optional[User] = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> bool:
    """
    Зависимость для включения неактивных объектов.
    Возвращает булевое значение - результат функции.
    """
    return await _is_manager_or_admin(cafe_id, current_user, session)


async def require_manager_or_admin(
    cafe_id: int,
    current_user: User,
    session: AsyncSession,
) -> User:
    """
    Зависимость для вызова ошибки если пользователь не имеет прав.
    Возвращает пользователя.
    """
    if not await _is_manager_or_admin(cafe_id, current_user, session):
        raise HTTPException(status_code=401, detail='Необходима авторизация')  # указал 401 потому что в спецификации нет 403
    return current_user


async def is_admin_or_manager(
        cafe: Cafe | None,
        current_user: User,
) -> bool:
    """Функция проверки пользователя на статус админа или менеджера кафе."""
    # Если пользователь - админ, то возвращаем True
    if current_user.is_superuser:
        return True
    # Если пользователь есть в списке менеджеров кафе
    if cafe is not None and current_user in cafe.managers:
        return True
    # Если ничего не нашли возвращаем False
    return False


async def check_admin_or_manager(
        cafe: Cafe,
        current_user: User,
) -> None:
    """Функция валидации статуса пользователя."""
    if not await is_admin_or_manager(cafe=cafe, current_user=current_user):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Необходима авторизация'
        )
