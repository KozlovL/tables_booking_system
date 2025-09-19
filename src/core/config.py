from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    app_title: str = 'Бронирование столиков'
    database_url: str

    class Config:
        """Конфигурация для загрузки переменных окружения."""

        env_file = '.env'


settings = Settings()
