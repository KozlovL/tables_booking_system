
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.auth import get_current_user, require_admin
from src.core.db import get_async_session
from src.crud.cafe import cafe_crud
from src.models.cafe import Cafe as CafeModel
from src.models.user import User
from src.schemas.cafe import CafeCreate, CafeRead, CafeUpdate

router = APIRouter(prefix="/cafes", tags=["Кафе"])


@router.post("",
             response_model=CafeRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)]
             )
async def create_cafe(
    payload: CafeCreate,
    session: AsyncSession = Depends(get_async_session),
):
    photo_url = payload.photo if payload.photo else None
    cafe = await cafe_crud.create_with_managers(
        payload,
        session,
        photo_url=photo_url
    )
    return cafe


@router.get('',
            response_model=list[CafeRead],
            status_code=status.HTTP_200_OK,
            )
async def list_cafes(
    show_all: bool = Query(False,
                           description='Показать все кафе '
                                       '(Неактивные только для админа)',
                           ),
    limit: int | None = Query(None, ge=1),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    # если пользователь не админ → всегда только активные
    only_active = True
    if current_user.is_superuser:
        only_active = not show_all

    cafes = await cafe_crud.get_multi_filtered(
        session,
        only_active=only_active,
    )
    return cafes


@router.get(
    '/{cafe_id}',
    response_model=CafeRead,
    status_code=status.HTTP_200_OK
)
async def get_cafe(
    cafe_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(CafeModel)
        .options(selectinload(CafeModel.managers))   # <— ключевой момент
        .where(CafeModel.id == cafe_id)
    )
    res = await session.execute(stmt)
    cafe = res.scalar_one_or_none()
    if not cafe:
        raise HTTPException(404, 'Cafe not found')

    if cafe.active or current_user.is_superuser:
        return cafe

    raise HTTPException(403, 'Not enough permissions')


@router.patch("/{cafe_id}",
              response_model=CafeRead,
              status_code=status.HTTP_200_OK,
              dependencies=[Depends(require_admin)]
              )
async def update_cafe(
        cafe_id: int,
        payload: CafeUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(require_admin),
):
    cafe = await cafe_crud.get(cafe_id, session)
    if not cafe:
        raise HTTPException(404, 'Cafe not found')

        # 2. Обработка фото (base64 → путь)
    update_data = payload.model_dump(exclude_unset=True)
    photo_url = None
    if 'photo' in update_data and update_data['photo']:
            photo_url = update_data['photo']

    cafe = await cafe_crud.update_with_managers(
        cafe,
        payload,
        session,
        photo_url=photo_url,
    )
    return cafe
