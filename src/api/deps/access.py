from src.core.exceptions import PermissionDeniedError
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
        raise PermissionDeniedError

