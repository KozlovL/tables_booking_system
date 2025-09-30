from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_title: str = 'Бронирование столиков'
    app_description: str = 'Проект «Бронирование мест в кафе»'
    database_url: str
    secret: str
    jwt_algorithm: str
    access_token_expire_min: int = 120
    bcrypt_rounds: int = 12
    first_superuser_username: Optional[str] = None
    first_superuser_phone: Optional[str] = None
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    # для Postgres (на проде)
    db_dialect: Optional[str] = None
    db_host: Optional[str] = 'localhost'
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_db: str | None = None
    postgres_host: str | None = None
    postgres_port: int | None = None

    class Config:
        """Конфигурация для загрузки переменных окружения."""

        env_file = '.env'


settings = Settings()
