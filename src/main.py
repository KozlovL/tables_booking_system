from fastapi import FastAPI
from core.config import settings


# Создание объекта приложения.
app = FastAPI(title=settings.app_title)


@app.get('/')
def read_root():
    return {'Hello': 'FastAPI'}
