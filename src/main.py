from fastapi import FastAPI

from core.config import settings

# Создание объекта приложения.
app = FastAPI(title=settings.app_title)


@app.get('/')
def read_root() -> dict[str, str]:
    """Корневой endpoint для проверки работы API."""
    return {'Hello': 'FastAPI'}
