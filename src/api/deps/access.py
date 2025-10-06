from fastapi import HTTPException

from src.models import User


def can_view_inactive(
    cafe_id: int | None,
    current_user: User,
) -> bool:
    """Возвращает True если админ или менеджер кафе"""
    if current_user.is_superuser:
        return True
    if cafe_id is not None:
        return cafe_id in current_user.managed_cafe_ids
    return bool(current_user.managed_cafe_ids)


def require_manager_or_admin(
    cafe_id: int,
    current_user: User,
) -> None:
    """
    Проверяет, имеет ли текущий пользователь права на управление указанным кафе
    """
    if (not current_user.is_superuser
       and cafe_id not in current_user.managed_cafe_ids):
        raise HTTPException(403, 'Доступ запрещен')  # подставить кастомный


# def is_admin_or_manager(
#         cafe: Cafe | None,
#         current_user: User,
# ) -> bool:
#     """Функция проверки пользователя на статус админа или менеджера кафе."""
#     # Если пользователь - админ, то возвращаем True
#     if current_user.is_superuser:
#         return True
#     # Если пользователь есть в списке менеджеров кафе
#     if cafe is not None and current_user in cafe.managers:
#         return True
#     # Если ничего не нашли возвращаем False
#     return False


# async def check_admin_or_manager(
#         cafe: Cafe,
#         current_user: User,
# ) -> None:
#     """Функция валидации статуса пользователя."""
#     if not await is_admin_or_manager(cafe=cafe, current_user=current_user):
#         raise HTTPException(
#             status_code=HTTPStatus.UNAUTHORIZED,
#             detail='Необходима авторизация'
#         )
