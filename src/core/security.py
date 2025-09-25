# src/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import bcrypt
from jose import jwt

from src.core.config import settings

# ---------- PASSWORDS (bcrypt) ----------


def get_password_hash(password: str) -> str:
    """Возвращает bcrypt-хэш (str). rounds управляем через settings.bcrypt_rounds.
    """
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    hashed: bytes = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")  # хранить в БД как str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль против сохранённого bcrypt-хэша.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False

# ---------- JWT ----------


def create_access_token(
    subject: str | int,
    expires_minutes: Optional[int] = None,
    extra_claims: Optional[dict[str, Any]] = None,
) -> str:
    if expires_minutes is None:
        expires_minutes = settings.access_token_expire_min

    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(
            minutes=expires_minutes))
                   .timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.secret,
                       algorithm=settings.jwt_algorithm,
                       )
    return token


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret,
                      algorithms=[settings.jwt_algorithm],
                      )
