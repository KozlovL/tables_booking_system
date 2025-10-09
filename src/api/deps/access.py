from src.core.exceptions import PermissionDeniedError
from src.models import BookingModel, BookingStatus, User


def can_view_inactive(
    cafe_id: int | None,
    current_user: User,
) -> bool:
    """Возвращает True если админ или менеджер кафе."""
    if current_user.is_superuser:
        return True
    if cafe_id is not None:
        return cafe_id in current_user.managed_cafe_ids
    return bool(current_user.managed_cafe_ids)


def require_manager_or_admin(
    cafe_id: int,
    current_user: User,
) -> None:
    """Проверка прав текущего пользователя на управление указанным кафе."""
    if (not current_user.is_superuser
       and cafe_id not in current_user.managed_cafe_ids):
        raise PermissionDeniedError


def can_view_inactive_booking(
    booking: BookingModel,
    user: User,
) -> bool:
    """Проверяет доступ к неактивным бронированиям."""
    return (user.is_superuser or booking.cafe_id in
            user.managed_cafe_ids or booking.user_id == user.id)


def can_edit_booking(booking: BookingModel, user: User) -> bool:
    """Определяет, может ли пользователь редактировать бронирование."""
    if booking.user_id == user.id:
        return booking.active and booking.status != BookingStatus.CANCELLED

    if user.is_superuser:
        return True

    if booking.cafe_id in user.managed_cafe_ids:
        return True

    return False
