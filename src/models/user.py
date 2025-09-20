from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from src.core.db import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    """Модель пользователя для базы данных."""

    pass
