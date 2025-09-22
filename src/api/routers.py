from fastapi import APIRouter

from .endpoints import (
    user_router, cafe
)

main_router = APIRouter()
main_router.include_router(user_router)
main_router.include_router(cafe.router)
