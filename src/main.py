from fastapi import FastAPI

from src.api.routers import main_router
from src.core.config import settings
from src.core.init_db import create_first_superuser

app = FastAPI(title=settings.app_title)

app.include_router(main_router)


@app.on_event('startup')
async def startup() -> None:
    """Функция запускается при старте приложения, создает суперпользователя."""
    await create_first_superuser()
