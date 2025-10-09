from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import can_view_inactive, require_manager_or_admin
from src.api.validators import cafe_exists, get_action_or_404, get_cafe_or_404
from src.core.auth import get_current_user
from src.core.db import get_async_session
from src.core.exceptions import ResourceNotFoundError
from src.core.logger import log_request, logger
from src.crud.action import action_crud
from src.models.user import User
from src.schemas.action import ActionCreate, ActionUpdate, ActionWithCafe

router = APIRouter(prefix='/actions', tags=['Акции'])


@log_request()
@router.get(
    "",
    response_model=List[ActionWithCafe],
    summary='Получение списка акций '
            '(только для администратора и менеджера,'
            ' пользователь - только активные)',
)
async def get_actions(
    show_all: Optional[bool] = Query(False),
    cafe_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> List[ActionWithCafe]:
    """Получение списка акций."""
    cafe = None
    if cafe_id is not None:
        cafe = await get_cafe_or_404(cafe_id=cafe_id, session=session)

    has_permission_for_inactive = can_view_inactive(cafe_id, current_user)

    active_only = not (show_all is True and has_permission_for_inactive)

    actions = await action_crud.get_actions_with_access_control(
        session=session,
        cafe=cafe,
        active_only=active_only,
        current_user=current_user,
    )

    logger.info(
        'Получен список акций',
        username=current_user.username,
        user_id=current_user.id,
        details={
            'count': len(actions),
            'cafe_id': cafe_id,
            'show_all': show_all,
            'active_only': active_only
        },
    )
    return actions


@log_request()
@router.post(
    "",
    response_model=ActionWithCafe,
    status_code=201,
    summary='Создание акции (только для администратора и менеджера)',
)
async def create_action(
        action: ActionCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
) -> ActionWithCafe:
    """Создание акции."""
    await cafe_exists(action.cafe_id, session)
    require_manager_or_admin(action.cafe_id, current_user)
    action_obj = await action_crud.create(session, action)

    logger.info(
        'Создана акция',
        username=current_user.username,
        user_id=current_user.id,
        details={
            'action_id': action_obj.id,
            'cafe_id': action.cafe_id,
            'title': action.title
        },
    )
    return action_obj


@log_request()
@router.get(
    "/{action_id}",
    response_model=ActionWithCafe,
    summary='Получение акции по ID '
            '(только для администратора и менеджера, '
            'пользователь - только активные)',
)
async def get_action(
        action_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
) -> ActionWithCafe:
    """Получение акции по ID."""
    action_obj = await get_action_or_404(action_id, session)
    include_inactive = can_view_inactive(action_obj.cafe_id, current_user)
    if not include_inactive and not action_obj.active:
        raise ResourceNotFoundError('Акция')

    logger.info(
        'Получена акция по ID',
        username=current_user.username,
        user_id=current_user.id,
        details={'action_id': action_id},
    )
    return action_obj


@log_request()
@router.patch(
    "/{action_id}",
    response_model=ActionWithCafe,
    summary='Обновление акции по ID (только для администратора и менеджера)',
)
async def update_action(
        action_id: int,
        action_update: ActionUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
) -> ActionWithCafe:
    """Обновление акции по ID."""
    action_obj = await get_action_or_404(action_id, session)
    require_manager_or_admin(action_obj.cafe_id, current_user)

    if (action_update.cafe_id is not None and
            action_update.cafe_id != action_obj.cafe_id):
        await cafe_exists(action_update.cafe_id, session)
        require_manager_or_admin(action_update.cafe_id, current_user)

    updated_action = await action_crud.update(
        session, action_obj, action_update)

    logger.info(
        'Обновлена акция',
        username=current_user.username,
        user_id=current_user.id,
        details={
            'action_id': action_id,
            'cafe_id': action_obj.cafe_id,
            'updated_fields': list(
                action_update.model_dump(exclude_unset=True).keys())
        },
    )
    return updated_action
