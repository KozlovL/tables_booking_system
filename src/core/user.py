# import logging
# from typing import AsyncGenerator, Optional, Union
#
# from fastapi import Depends, Request
# from fastapi_users import (
#     BaseUserManager,
#     FastAPIUsers,
#     IntegerIDMixin,
#     InvalidPasswordException,
# )
# from fastapi_users.authentication import (
#     AuthenticationBackend,
#     BearerTransport,
#     JWTStrategy,
# )
# from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.core.config import settings
# from src.core.db import get_async_session
# from src.models.user import User
# from src.schemas.user import UserCreate
#
# logger = logging.getLogger(__name__)
#
#
# async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> (
#         AsyncGenerator)[SQLAlchemyUserDatabase, None]:
#     """Возвращает объект базы данных пользователей для FastAPI Users."""
#     yield SQLAlchemyUserDatabase(session, User)
#
#
# bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')
#
#
# def get_jwt_strategy() -> JWTStrategy:
#     """Создаёт стратегию JWT для аутентификации пользователей.
#
#     Возвращает объект JWTStrategy с секретным ключом и временем жизни токена.
#     """
#     return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)
#
#
# auth_backend = AuthenticationBackend(
#     name='jwt',
#     transport=bearer_transport,
#     get_strategy=get_jwt_strategy,
# )
#
#
# class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
#     """Менеджер пользователей."""
#
#     use_bcrypt = False
#
#     MIN_PASSWORD_LENGTH = 3
#
#     async def validate_password(
#         self,
#         password: str,
#         user: Union[UserCreate, User],
#     ) -> None:
#         """Валидация пароля."""
#         if len(password) < self.MIN_PASSWORD_LENGTH:
#             raise InvalidPasswordException(
#                 reason='Пароль должен быть длинее 3 символов',
#             )
#         if user.email in password:
#             raise InvalidPasswordException(
#                 reason='Пароль не может содержать e-mail',
#             )
#
#     async def on_after_register(
#             self, user: User, request: Optional[Request] = None,
#     ) -> None:
#         """Вызывается после регистрации пользователя.
#
#         Можно использовать для логирования или уведомлений.
#         """
#         print(f"Пользователь {user.email} успешно зарегистрирован")
#
#
# async def get_user_manager(
#     user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
# ) -> AsyncGenerator[UserManager, None]:
#     """Возвращает менеджер пользователей."""
#     yield UserManager(user_db)
#
#
# fastapi_users = FastAPIUsers[User, int](
#     get_user_manager,
#     [auth_backend],
# )
#
# current_user = fastapi_users.current_user(active=True)
# current_superuser = fastapi_users.current_user(active=True, superuser=True)
