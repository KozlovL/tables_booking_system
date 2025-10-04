# src/api/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user, require_admin
from src.core.db import get_async_session
from src.core.security import get_password_hash
from src.crud.user import user_crud
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate
from src.api.validators import check_unique_fields

router = APIRouter(prefix="/users", tags=["users"])


@router.post("",
             response_model=UserRead,
             status_code=status.HTTP_201_CREATED,
             )
async def create_user_endpoint(payload: UserCreate,
                               session: AsyncSession =
                               Depends(get_async_session),
                               current_admin=Depends(require_admin),
                               ):
    user = await user_crud.create(payload, session)
    await session.commit()
    await session.refresh(user)
    return user


@router.get("/me", response_model=UserRead, status_code=status.HTTP_200_OK)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserUpdate, status_code=status.HTTP_200_OK)
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # сущность из БД
    db_user = await user_crud.get(current_user.id, session)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    data = payload.model_dump(exclude_unset=True)

    # если пришёл пароль — хэшируем
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))

    # ограничим список меняемых колонок (на всякий случай)
    updatable = {"username", "email", "phone", "tg_id", "hashed_password"}
    await user_crud.update(db_user, data, session, updatable_fields=updatable)

    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.patch("/{user_id}",
              response_model=UserUpdate,
              status_code=status.HTTP_200_OK,
              )
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_admin=Depends(require_admin),
):
    db_user = await user_crud.get(user_id, session)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.dict(exclude_unset=True)

    # Если передан пароль — хэшируем
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    unique_fields = {'username', 'email', 'phone', 'tg_id'}
    fields_to_check = {
        k: v for k, v in update_data.items() if k in unique_fields
    }

    if fields_to_check:  # выдавало ошибку 500
        await check_unique_fields(
            session=session,
            model=User,
            exclude_id=user_id,
            **fields_to_check
        )

    updated_user = await user_crud.update(db_user, update_data, session)
    await session.commit()
    await session.refresh(updated_user)
    return updated_user


@router.get("/{user_id}",
            response_model=UserRead,
            status_code=status.HTTP_200_OK,
            )
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_admin=Depends(require_admin),
):
    db_user = await user_crud.get(user_id, session)
    return db_user
