"""JWT-утилиты и заглушка безопасности для учебной версии."""
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from jose import JWTError, jwt

from app.core.config import settings


def create_token(subject: str | UUID, expires_delta: timedelta, token_type: str = "access") -> str:
    payload = {
        "sub": str(subject),
        "type": token_type,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: str | UUID) -> str:
    return create_token(user_id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(user_id: str | UUID) -> str:
    return create_token(user_id, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise ValueError("Invalid or expired token")
