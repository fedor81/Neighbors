"""SQLAlchemy engine и session factory. PostgreSQL + PostGIS в проде, SQLite для тестов."""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# lazy-engine: не требует установленного драйвера БД при импорте (важно для каркаса/тестов)
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    return _engine


class _LazySessionLocal:
    def __call__(self):
        return sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)()

    def __getattr__(self, name):
        return getattr(self(), name)


SessionLocal = _LazySessionLocal()


def get_db():
    """FastAPI dependency: сессия БД на запрос."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
