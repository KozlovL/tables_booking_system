from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.crud.dish import dish_crud
from src.schemas.dish import DishDB

router = APIRouter(prefix='/dishes', tags=['Блюдо'])


@router.get(
    '/',
    response_model=list[DishDB],
    response_model_exclude_none=True,
    # dependencies=[Depends(current_superuser)]
    summary='Получение списка всех блюд',
)
async def get_all_dishes(
        session: AsyncSession = Depends(get_async_session)
):
    return await dish_crud.get_multi(session)
