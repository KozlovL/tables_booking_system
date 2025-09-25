# src/core/auth.py
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_async_session
from src.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)  # не падаем, если заголовка нет


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Security(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = creds.credentials
    try:
        payload = jwt.decode(
            token, settings.secret, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    res = await session.execute(select(User).where(User.id == int(sub)))
    user = res.scalars().one_or_none()

    if not user or not user.active:
        raise HTTPException(status_code=401, detail="User inactive or not found")
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user
