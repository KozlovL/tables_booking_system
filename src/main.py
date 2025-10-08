from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routers import main_router
from src.core.config import settings
from src.core.exceptions import AppException
from src.core.init_db import create_first_superuser

app = FastAPI(title=settings.app_title)

app.include_router(main_router, prefix="/api/v1")


@app.on_event('startup')
async def startup() -> None:
    """Функция запускается при старте приложения, создает суперпользователя."""
    if settings.db_dialect == "sqlite":
        await create_first_superuser()
    else: pass

