from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.validators import check_unique_fields
from src.core.auth import get_current_user, require_admin
from src.core.db import get_async_session
from src.core.logger import log_request, logger
from src.core.security import get_password_hash
from src.crud.user import user_crud
from src.models.user import User
from src.schemas.user import UserCreate, UserRead, UserUpdate
from src.api.validators import check_unique_fields
from src.core.exceptions import (ResourceNotFoundError,
                                 DuplicateError
                                 )
router = APIRouter(prefix="/users", tags=["users"])


@log_request()
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



@log_request()
@router.get(
    '/me',
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary='Получение данных текущего пользователя '
            '(доступно только текущему пользователю)',
    )
async def read_me(
    current_user: UserShort = Depends(get_current_user),
) -> UserRead:
    """Получение данных текущего пользователя."""
    logger.info(
        'Получены данные текущего пользователя',
        username=current_user.username,
        user_id=current_user.id,
    )
    return current_user


@log_request()
@router.patch(
    '/me',
    response_model=UserUpdate,
    status_code=status.HTTP_200_OK,
    summary='Обновление данных текущего пользователя '
            '(доступно только текущему пользователю)',
    )
async def update_me(
    payload: UserUpdate,
    current_user: UserShort = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> UserUpdate:
    """Обновление данных текущего пользователя."""
    db_user = await user_crud.get(current_user.id, session)
    if not db_user:
      logger.warning(
            'Попытка обновления несуществующего пользователя',
            username=current_user.username,
            user_id=current_user.id,
        )
        raise ResourceNotFoundError("Пользователь")

    data = payload.model_dump(exclude_unset=True)

    # если пришёл пароль — хэшируем
    if "password" in data:
        data["hashed_password"] = get_password_hash(data.pop("password"))



    # ограничим список меняемых колонок (на всякий случай)
    updatable = {"username", "email", "phone", "tg_id", "hashed_password"}

    unique_fields = {'username', 'email', 'phone', 'tg_id'}
    fields_to_check = {
        k: v for k, v in data.items() if k in unique_fields
    }
    if fields_to_check:  # выдавало ошибку 500
        await check_unique_fields(
            session=session,
            model=User,
            exclude_id=db_user.id,
            **fields_to_check
        )

    db_user = await  user_crud.update(db_user,
                                      data,
                                      session,
                                      updatable_fields=updatable
                                      )
    await session.commit()
    await session.refresh(updated_user)

    logger.info(
        'Обновлены данные пользователя',
        username=current_user.username,
        user_id=current_user.id,
        details={
            'updated_fields': list(data.keys()),
            'target_user_id': db_user.id,
        },
    )
    return updated_user


@log_request()
@router.patch(
    '/{user_id}',
    response_model=UserUpdate,
    status_code=status.HTTP_200_OK,
    summary='Обновление данных пользователя по ID (только для администратора)',
)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_admin: UserShort = Depends(require_admin),
) -> UserUpdate:
    """Обновление данных пользователя админом."""
    db_user = await user_crud.get(user_id, session)
    if not db_user:
        logger.warning(
            'Попытка обновления несуществующего пользователя',
            username=current_admin.username,
            user_id=current_admin.id,
            details={'target_user_id': user_id},
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )

    update_data = payload.dict(exclude_unset=True)
    if 'password' in update_data:
        update_data['hashed_password'] = get_password_hash(
            update_data.pop('password'),
        )

    unique_fields = {'username', 'email', 'phone', 'tg_id'}
    fields_to_check = {
        key: value
        for key, value in update_data.items()
        if key in unique_fields
    }
    if fields_to_check:
        await check_unique_fields(
            session=session,
            model=User,
            exclude_id=user_id,
            **fields_to_check,
        )

    updated_user = await user_crud.update(db_user, update_data, session)
    await session.commit()
    await session.refresh(updated_user)

    logger.info(
        'Обновлены данные пользователя админом',
        username=current_admin.username,
        user_id=current_admin.id,
        details={
            'updated_fields': list(update_data.keys()),
            'target_user_id': db_user.id,
        },
    )
    return updated_user


@log_request()
@router.get(
    '/{user_id}',
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary='Получение пользователя по ID (только для администратора)',
)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_admin: UserShort = Depends(require_admin),
) -> UserRead:
    """Получение данных пользователя админом."""
    db_user = await user_crud.get(user_id, session)
    if db_user is None:
        raise ResourceNotFoundError("Пользователь")
    return db_user

    logger.info(
        'Получены данные пользователя админом',
        username=current_admin.username,
        user_id=current_admin.id,
        details={'target_user_id': user_id},
    )
    return db_user
