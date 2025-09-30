from http import HTTPStatus

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from src.models import User, cafe_managers_table, Cafe


async def _is_manager_or_admin(
    cafe_id: int,
    user: User,
    session: AsyncSession
) -> bool:
    """
    Проверяет, имеет ли пользователь права администратора или менеджера
    для указанного кафе.

    Возвращает True, если пользователь:
        - является суперпользователем (глобальный администратор), или
        - назначен менеджером данного кафе (наличие записи в cafe_managers_table).

    В противном случае возвращает False.
    """
    if user.is_superuser:
        return True
    query = select(exists().where(
        cafe_managers_table.c.user_id == user.id,
        cafe_managers_table.c.cafe_id == cafe_id
    ))
    return await session.scalar(query)


async def get_include_inactive(
    cafe_id: int,
    current_user: User,
    session: AsyncSession,
) -> bool:
    """
    Определяет, следует ли включать неактивные объекты (столы, блюда и т.д.) в ответ.

    Возвращает True, если текущий пользователь имеет права на управление кафе
    (является суперпользователем или менеджером кафе), иначе — False.

    Используется как зависимость в эндпоинтах для динамического включения/исключения
    неактивных записей в зависимости от прав доступа.
    """
    return await _is_manager_or_admin(cafe_id, current_user, session)


async def require_manager_or_admin(
    cafe_id: int,
    current_user: User,
    session: AsyncSession,
):
    """
    Проверяет, имеет ли текущий пользователь права на управление указанным кафе

    Доступ разрешён, если пользователь:
        - является суперпользователем (глобальный администратор), или
        - назначен менеджером данного кафе.

    В случае отсутствия прав вызывает HTTP 403 Forbidden.
    """
    if not await _is_manager_or_admin(cafe_id, current_user, session):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен'
        )  # поставил 403 потому что так правильно


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
