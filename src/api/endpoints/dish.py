from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps.access import can_view_inactive, require_manager_or_admin
from src.api.validators import (
    check_dish_name_duplicate,
    get_dish_or_404, get_cafe_or_404,
)
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.crud.dish import dish_crud
from src.models import User
from src.schemas.dish import DishCreate, Dish, DishUpdate

router = APIRouter(prefix='/dishes', tags=['Блюдо'])


@router.get(
    '',
    response_model=list[Dish],
    response_model_exclude_none=True,
    summary='Получение списка всех блюд',
)
async def get_all_dishes(
        session: AsyncSession = Depends(get_async_session),
        show_all: bool | None = None,
        cafe_id: int | None = None,
        current_user: User = Depends(get_current_user)
):
    cafe = None
    if cafe_id is not None:
        cafe = await get_cafe_or_404(cafe_id=cafe_id, session=session)

    has_permission_for_inactive = can_view_inactive(cafe_id, current_user)

    active_only = not (show_all is True and has_permission_for_inactive)

    return await dish_crud.get_dishes_with_access_control(
        session=session,
        cafe=cafe,
        active_only=active_only,
        current_user=current_user,
    )


@router.post(
    '',
    response_model=Dish,
    response_model_exclude_none=True,
    summary='Создание блюда'
)
async def create_dish(
        dish: DishCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    cafe = await get_cafe_or_404(
        session=session,
        cafe_id=dish.cafe_id,
    )
    require_manager_or_admin(
        cafe_id=dish.cafe_id,
        current_user=current_user
    )
    await check_dish_name_duplicate(
        dish_name=dish.name,
        cafe=cafe,
        session=session,
    )
    new_dish = await dish_crud.create(obj_in=dish, session=session)
    return new_dish


@router.get(
    '/{dish_id}',
    response_model=Dish,
    response_model_exclude_none=True,
    summary='Получение блюда по ID'
)
async def get_dish_by_id(
        dish_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
):
    dish = await get_dish_or_404(
        dish_id=dish_id,
        session=session,
        extra_uploading=True
    )
    await get_cafe_or_404(cafe_id=dish.cafe_id, session=session)
    if can_view_inactive(
        cafe_id=dish.cafe_id,
        current_user=current_user
    ) or dish.active is True:
        return dish
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND,
        detail='Блюдо не найдено'
    )


@router.patch(
    '/{dish_id}',
    response_model=Dish,
    response_model_exclude_none=True,
    summary='Изменение блюда по ID'
)
async def update_dish(
        dish_id: int,
        new_dish: DishUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user),
):
    current_dish = await get_dish_or_404(dish_id, session)
    cafe = await get_cafe_or_404(
        cafe_id=current_dish.cafe_id,
        session=session
    )
    require_manager_or_admin(
        cafe_id=current_dish.cafe_id,
        current_user=current_user
    )
    new_cafe_id = new_dish.cafe_id
    # Если передали кафе и оно не совпадает с текущим
    if new_cafe_id is not None and new_cafe_id != cafe.id:
        cafe = await get_cafe_or_404(cafe_id=new_cafe_id, session=session)
    new_dish_name = new_dish.name
    if new_dish_name is not None and new_dish_name != current_dish.name:
        await check_dish_name_duplicate(
            dish_name=new_dish.name,
            cafe=cafe,
            session=session,
        )
    dish_result = await dish_crud.update(
        db_obj=current_dish,
        obj_in=new_dish,
        session=session,
    )
    return dish_result
