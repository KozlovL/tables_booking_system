

from src.crud.base import CRUDBase
from src.models.cafe import Cafe


class CRUDCafe(CRUDBase):
    pass


cafe_crud = CRUDCafe(Cafe)
