run:
uvicorn app.main:app --reload --port 8000

migrate:
alembic revision --autogenerate -m "schema"

upgrade:
alembic upgrade head

test:
pytest tests -v

up:
docker compose up -d
