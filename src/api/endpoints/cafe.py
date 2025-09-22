from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db import get_async_session
from src.schemas.cafe import CafeCreate, CafeRead
from src.models.user import User
from src.models.cafe import Cafe as CafeModel
from src.crud.cafe import cafe_crud
from src.utils.images import save_base64_image, file_url_to_base64

router = APIRouter(prefix="/cafes", tags=["Кафе"])

@router.post("", response_model=CafeRead, status_code=status.HTTP_201_CREATED)
async def create_cafe(payload: CafeCreate, session: AsyncSession = Depends(get_async_session)):
    photo_url = None
    if payload.photo:
        photo_url = save_base64_image(payload.photo)

    # 1) создаём объект кафе и добавляем в сессию
    new_cafe = CafeModel(
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
        description=payload.description,
        photo=photo_url,
    )
    session.add(new_cafe)

    # 2) загружаем ORM-пользователей по ID
    managers = []
    if payload.managers:
        res = await session.execute(select(User).where(User.id.in_(payload.managers)))
        managers = list(res.scalars())
        found_ids = {u.id for u in managers}
        missing = [mid for mid in payload.managers if mid not in found_ids]
        if missing:
            raise HTTPException(400, detail={"missing_manager_ids": missing})

    # 3) ПРИСВАИВАЕМ ДО flush/commit — так не будет ленивой загрузки
    if managers:
        # можно так:
        new_cafe.managers = managers
        # или так:
        # new_cafe.managers.extend(managers)

    # 4) фиксируем и коммитим
    await session.flush()  # получишь new_cafe.id
    new_id = new_cafe.id
    await session.commit()

    # 5) перечитать для ответа с подзагрузкой менеджеров
    res = await session.execute(
        select(CafeModel)
        .options(selectinload(CafeModel.managers))
        .where(CafeModel.id == new_id)
    )
    return res.scalar_one()

