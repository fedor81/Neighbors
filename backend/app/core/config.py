"""Настройки приложения (Pydantic Settings)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "Neighbors"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # БД / Redis
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/neighbors"
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # SMS-заглушка (учебный MVP: код всегда "1234", см. utils/sms.py)
    SMS_PROVIDER: str = "stub"
    VERIFICATION_CODE_TTL_SECONDS: int = 300
    VERIFICATION_MAX_ATTEMPTS: int = 5

    # Холдирование залога / сроки
    BOOKING_APPROVAL_TIMEOUT_HOURS: int = 24
    REVIEW_VISIBILITY_DELAY_DAYS: int = 3

    # S3 / MinIO
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_BUCKET: str = "neighbors-items"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"

    # Геоданные
    DEFAULT_LOCAL_RADIUS_KM: float = 1.5

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
