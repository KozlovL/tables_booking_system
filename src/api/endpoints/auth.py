from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.core.logger import log_request, logger
from src.core.security import create_access_token, verify_password
from src.models.user import User
from src.schemas.auth import LoginRequest, TokenResponse
from src.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@log_request()
@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Вход пользователя и выдача токена."""
    identifier: str = payload.name.strip()
    if "@" in identifier:
        lookup = select(User).where(User.email == identifier.lower())
    else:
        lookup = select(User).where(User.phone == identifier)

    res = await session.execute(lookup)
    user: User | None = res.scalar_one_or_none()

    if not user or not user.active:
        logger.warning(
            "Неудачная попытка входа",
            details={"identifier": identifier},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
        )

    if not verify_password(payload.password, user.hashed_password):
        logger.warning(
            "Неверный пароль",
            username=user.username,
            user_id=user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
        )

    token: str = create_access_token(subject=user.id)
    logger.info("Успешный вход", username=user.username, user_id=user.id)
    return TokenResponse(access_token=token)


@log_request()
@router.post(
    "/logout",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def logout(
    current_user: UserRead = Depends(get_current_user),
) -> JSONResponse:
    """Выход пользователя."""
    logger.info(
        "Выход пользователя",
        username=current_user.username,
        user_id=current_user.id,
    )
    return JSONResponse(
        content={
            "message": f"Пользователь {current_user.username} успешно вышел",
        },
        status_code=status.HTTP_200_OK,
    )
