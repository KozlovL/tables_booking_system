from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_async_session
from src.core.logger import logger
from src.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """Возвращает текущего пользователя по токену."""
    if not creds or creds.scheme.lower() != 'bearer':
        logger.warning('Попытка доступа без токена')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
        )

    token = creds.credentials
    try:
        payload = jwt.decode(
            token,
            settings.secret,
            algorithms=[settings.jwt_algorithm],
        )
        sub = payload.get('sub')
        if not sub:
            logger.warning('Неверный токен: отсутствует sub')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token',
            )
    except JWTError:
        logger.warning('Неверный токен: JWTError')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
        )

    res = await session.execute(select(User).where(User.id == int(sub)))
    user: User | None = res.scalars().one_or_none()

    if not user or not user.active:
        logger.warning(
            'Пользователь не найден или неактивен',
            details={'user_id': sub},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User inactive or not found',
        )

    logger.info(
        'Аутентификация успешна',
        details={'user_id': user.id, 'username': user.username},
    )
    return user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Проверяет, что пользователь администратор."""
    if not current_user.is_superuser:
        logger.warning(
            'Доступ запрещён: требуется админ',
            details={'user_id': current_user.id},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Admin privileges required',
        )

    logger.info(
        'Админ проверка пройдена',
        details={'user_id': current_user.id},
    )
    return current_user
