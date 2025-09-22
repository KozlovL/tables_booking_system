from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.cafe import Cafe


class CRUDCafe(CRUDBase):
    pass



cafe_crud = CRUDCafe(Cafe)
