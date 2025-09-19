from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_title: str = 'Бронирование столиков'
    app_description: str = 'Проект «Бронирование мест в кафе»'
    database_url: str
    secret: str
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        """Конфигурация для загрузки переменных окружения."""

        env_file = '.env'


settings = Settings()
