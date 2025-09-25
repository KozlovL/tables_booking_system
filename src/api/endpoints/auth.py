from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.core.security import create_access_token, verify_password
from src.models.user import User
from src.schemas.auth import LoginRequest, TokenResponse
from src.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
        payload: LoginRequest,
        session: AsyncSession = Depends(get_async_session),
):
    identifier = payload.name.strip()
    # если есть '@' — это email, иначе — телефон
    if "@" in identifier:
        lookup = select(User).where(User.email == identifier.lower())
    else:
        lookup = select(User).where(User.phone == identifier)

    res = await session.execute(lookup)
    user: User | None = res.scalar_one_or_none()

    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.post("/logout",
             response_model=UserRead,
             status_code=status.HTTP_200_OK,
             )
async def logout(
        current_user:
        UserRead = Depends(get_current_user),
):
    """Logout current user.
    (говорим клиенту забыть токен)
    """
    return JSONResponse(
        content={"message": f"User {current_user.username} "
                            f"logged out successfully"},
        status_code=200,
    )
