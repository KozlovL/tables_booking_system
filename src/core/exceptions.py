# src/exceptions.py

class BusinessException(Exception):
    """Базовый класс для бизнес-исключений в приложении."""
    @property
    def detail(self) -> str:
        return self.args[0] if self.args else "Business logic error"


class UserAlreadyExists(BusinessException):
    """Выбрасывается, когда пользователь с такими уникальными данными уже существует."""
    pass


class InvalidUserData(BusinessException):
    """Выбрасывается при невалидных данных пользователя """
    pass

class ManagersNotFoundError(BusinessException):
    """Выбрасывается когда менеджеры не найдены create/update кафе """
    pass