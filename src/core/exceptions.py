# src/exceptions.py

from http import HTTPStatus


class AppException(Exception):
    """Базовые класс ошибок бизнес логики."""

    status_code: int = HTTPStatus.BAD_REQUEST
    detail: str = "Неверный формат запроса"
    code: str = "bad_request"

    def __init__(
        self,
        status_code: int | None = None,
        detail: str | None = None,
        code: str | None = None,

    ) -> None:
        """Инициализирует исключение приложения."""
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = detail
        if code is not None:
            self.code = code
        super().__init__(self.detail)


class NotAuthenticatedError(AppException):
    """Необходима авторизация."""

    status_code = HTTPStatus.UNAUTHORIZED
    detail = "Необходима авторизация"
    code = "unauthorized"


class PermissionDeniedError(AppException):
    """Недостаточно прав."""

    status_code = HTTPStatus.FORBIDDEN
    detail = "Недостаточно прав"
    code = "forbidden"


class ResourceNotFoundError(AppException):
    """Объект не найден в базе."""

    status_code = HTTPStatus.NOT_FOUND

    def __init__(self, resource_name: str) -> None:
        """Инициализирует ошибку ненайденного ресурса."""
        detail = f'{resource_name} не найдено'
        super().__init__(detail=detail, code="not_found")


class ConflictError(AppException):
    """Конфликт с существующими записями."""

    status_code = HTTPStatus.CONFLICT
    code = "conflict"


class DuplicateError(ConflictError):
    """Такая запись уже существует."""

    code = "duplicate"

    def __init__(
        self,
        entity: str | None = None,
        *,
        key: str | None = None,
        extra : str | None = None,
    ) -> None:
        """Создает исключение дублирования записи."""
        name = entity or "Объект"
        detail = f"{name} уже существует"
        super().__init__(detail=detail, code=self.code)
