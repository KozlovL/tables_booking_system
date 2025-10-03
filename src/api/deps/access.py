from http import HTTPStatus

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Cafe, User, cafe_managers_table


async def _is_manager_or_admin(
    cafe_id: int,
    user: User,
    session: AsyncSession,
) -> bool:
    """Проверяет, является ли пользователь админом или менеджером кафе."""
    if user.is_superuser:
        return True
    query = select(
        exists().where(
            cafe_managers_table.c.user_id == user.id,
            cafe_managers_table.c.cafe_id == cafe_id,
        ),
    )
    return await session.scalar(query)


async def get_include_inactive(
    cafe_id: int,
    current_user: User,
    session: AsyncSession,
) -> bool:
    """Определяет, включать ли неактивные объекты для пользователя."""
    return await _is_manager_or_admin(cafe_id, current_user, session)


async def require_manager_or_admin(
    cafe_id: int,
    current_user: User,
    session: AsyncSession,
) -> None:
    """Выбрасывает 403, если пользователь не админ/менеджер."""
    if not await _is_manager_or_admin(cafe_id, current_user, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен',
        )


async def is_admin_or_manager(
    cafe: Cafe | None,
    current_user: User,
) -> bool:
    """Проверяет, является ли пользователь админом или менеджером кафе."""
    if current_user.is_superuser:
        return True
    if cafe is not None and current_user in cafe.managers:
        return True
    return False


async def check_admin_or_manager(
    cafe: Cafe,
    current_user: User,
) -> None:
    """Выбрасывает 401, если пользователь не админ/менеджер."""
    if not await is_admin_or_manager(cafe=cafe, current_user=current_user):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Необходима авторизация',
        )
