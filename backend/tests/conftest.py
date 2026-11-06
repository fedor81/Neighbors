"""pytest fixtures: in-memory SQLite вместо PostgreSQL для тестов каркаса."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
