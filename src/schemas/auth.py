from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Схема для логина. Обязательно телефон или email."""

    name: str = Field(..., description="Email или телефон")
    password: str


class TokenResponse(BaseModel):
    """Выдается токен."""

    access_token: str
    token_type: str = "bearer"
