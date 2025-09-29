from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps.access import is_admin_or_manager, check_admin_or_manager
from src.api.validators import (
    check_dish_name_duplicate,
    get_dish_or_404, cafe_exists,
)
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.crud.dish import dish_crud
from src.models import User
from src.schemas.dish import DishCreate, Dish, DishUpdate

router = APIRouter(prefix='/dishes', tags=['Блюдо'])


@router.get(
    '/',
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
    # Список фильтров для запроса
    query_kwargs = {}
    # Если параметр show_all не был передан или пользователь не является
    # админом или менеджером кафе, то добавляем фильтр active=True
    if show_all is not True or not is_admin_or_manager(
        session=session,
        cafe_id=cafe_id,
        current_user=current_user,
    ):
        query_kwargs['active'] = True

    # Если был передан параметр cafe_id, то добавляем его как фильтр для запроса
    if cafe_id is not None:
        query_kwargs['cafe_id'] = cafe_id

    return await dish_crud.get_by_field(
        session=session,
        many=True,
        **query_kwargs,
    )


@router.post(
    '/',
    response_model=Dish,
    response_model_exclude_none=True,
    summary='Создание блюда'
)
async def create_dish(
        dish: DishCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
):
    await check_admin_or_manager(
        session=session,
        cafe_id=dish.cafe_id,
        current_user=current_user,
    )
    await check_dish_name_duplicate(
        dish.name,
        session=session,
    )
    await cafe_exists(
        dish.cafe_id,
        session,
    )
    new_dish = await dish_crud.create(dish, session)
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
    dish = await get_dish_or_404(dish_id, session)
    if is_admin_or_manager(
        session=session,
        cafe_id=dish.cafe_id,
        current_user=current_user,
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
    cafe_id = current_dish.cafe_id
    await cafe_exists(cafe_id, session)
    await check_admin_or_manager(
        session=session,
        cafe_id=cafe_id,
        current_user=current_user,
    )
    if new_dish.name is not None:
        await check_dish_name_duplicate(
            new_dish.name,
            session,
        )
    if new_dish.cafe_id is not None:
        await cafe_exists(
            cafe_id=new_dish.cafe_id,
            session=session,
        )
    dish_result = await dish_crud.update(
        current_dish,
        new_dish,
        session
    )
    return dish_result
