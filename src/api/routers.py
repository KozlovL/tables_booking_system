from fastapi import APIRouter

from .endpoints import auth_router, cafe_router, user_router, table_router

main_router = APIRouter()
main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(cafe_router)
main_router.include_router(table_router)
