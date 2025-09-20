from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import auth_backend, current_superuser, fastapi_users
from src.models import User
from src.schemas import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)

router.include_router(
    users_router,
    prefix='/users',
    tags=['users'],
)


@router.get('/users', response_model=List[UserRead], tags=['users'])
async def get_users(
    show_all: bool = Query(False, description='Показать всех пользователей'),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_superuser)
):
    """Получение списка пользователей (только для администратора)."""
    query = select(User)
    if not show_all:
        query = query.where(User.is_active is True)

    result = await session.execute(query)
    users = result.scalars().all()
    return users
