from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_include_inactive, require_manager_or_admin
from src.api.deps.access import check_admin_or_manager
from src.core.db import get_async_session
from src.core.auth import get_current_user
from src.crud.table import table_crud
from src.api.validators import (
    get_table_or_404,
    cafe_exists,
)
from src.schemas.table import Table, TableCreate, TableUpdate
from src.models.user import User

router = APIRouter(prefix='/cafe/{cafe_id}/tables', tags=['Столы'])


