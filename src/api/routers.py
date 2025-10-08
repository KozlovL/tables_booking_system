from fastapi import APIRouter

from .endpoints import (
    action_router,
    auth_router,
    cafe_router,
    dish_router,
    slot_router,
    table_router,
    user_router,
    booking_router
)

main_router = APIRouter()

main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(cafe_router)
main_router.include_router(table_router)
main_router.include_router(dish_router)
main_router.include_router(slot_router)
main_router.include_router(booking_router)
main_router.include_router(action_router)
