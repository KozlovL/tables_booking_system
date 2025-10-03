import inspect
import logging
from functools import wraps
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, Optional

from fastapi import Request

from src.core.constants import BACKUP_COUNT, LOG_FILE, MAX_BYTES


class ProjectLogger(logging.Logger):
    """Централизованный логгер с поддержкой контекста пользователя."""

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        """Инициализация логгера с именем и уровнем."""
        super().__init__(name, level)
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Настройка консольного и файлового обработчиков."""
        if self.handlers:
            return
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(username)s | '
            '%(user_id)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding='utf-8',
        )
        file_handler.setFormatter(formatter)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(file_handler)
        self.addHandler(console_handler)

    def _with_user(
        self,
        msg: str,
        username: Optional[str],
        user_id: Optional[int],
        details: Optional[Dict],
    ) -> tuple[str, dict]:
        """Формирует сообщение и словарь extra для логирования."""
        extra = {
            'username': username if username else 'SYSTEM',
            'user_id': user_id if user_id else '-',
        }
        if details:
            msg = f'{msg} | {details}'
        return msg, extra

    def info(
        self,
        msg: str,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Логирует информационное сообщение."""
        msg, extra = self._with_user(msg, username, user_id, details)
        super().info(msg, *args, extra=extra, **kwargs)

    def warning(
        self,
        msg: str,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Логирует предупреждение."""
        msg, extra = self._with_user(msg, username, user_id, details)
        super().warning(msg, *args, extra=extra, **kwargs)

    def error(
        self,
        msg: str,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Логирует ошибку."""
        msg, extra = self._with_user(msg, username, user_id, details)
        super().error(msg, *args, extra=extra, **kwargs)

    def debug(
        self,
        msg: str,
        username: Optional[str] = None,
        user_id: Optional[int] = None,
        details: Optional[Dict] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Логирует отладочное сообщение."""
        msg, extra = self._with_user(msg, username, user_id, details)
        super().debug(msg, *args, extra=extra, **kwargs)


logging.setLoggerClass(ProjectLogger)
logger: ProjectLogger = logging.getLogger('central_logger')  # type: ignore

logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.sql").setLevel(logging.WARNING)


def log_request(details: Optional[Dict] = None) -> Callable:
    """Декоратор логирования вызова эндпоинта FastAPI."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """Оборачивает функцию для логирования вызовов."""

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Логирует асинхронный вызов эндпоинта."""
            current_user = next(
                (
                    value
                    for value in kwargs.values()
                    if hasattr(value, 'username') and hasattr(value, 'id')
                ),
                None,
            )
            username = getattr(
                current_user, 'username', None) if current_user else None
            user_id = getattr(
                current_user, 'id', None) if current_user else None

            request: Optional[Request] = next(
                (v for v in kwargs.values() if isinstance(v, Request)), None,
            )
            path = request.url.path if request else 'unknown'
            method = request.method if request else 'unknown'

            logger.info(
                f'Вызван эндпоинт {func.__name__} [{method} {path}]',
                username=username,
                user_id=user_id,
                details=details,
            )
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """Логирует синхронный вызов функции."""
            logger.info(
                f'Вызван sync эндпоинт {func.__name__}',
                username='SYSTEM',
                user_id='-',
                details=details,
            )
            return func(*args, **kwargs)

        return (
            async_wrapper
            if inspect.iscoroutinefunction(func)
            else sync_wrapper)

    return decorator
