# Neighbors

Веб-сервис обмена вещами между соседями (ЖК / кампус): единая витрина предметов,
бронирование с залогом, внутренний чат, взаимные рейтинги, модерация споров.

## Артефакты проектирования
- [`Artifacts/UseCases.md`](Artifacts/UseCases.md) — спецификация UC-1…UC-10 + ER-диаграмма
- [`docs/API.md`](docs/API.md) — REST API (/api/v1, ~50 эндпоинтов)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — стек и ключевые решения

## Структура каркаса
```
backend/                  # FastAPI (Python 3.12)
├── app/
│   ├── main.py           # точка входа, CORS, подключение роутеров
│   ├── core/             # config (Pydantic Settings), security (JWT), database
│   ├── api/
│   │   ├── deps.py       # get_current_user, require_moderator
│   │   └── v1/           # auth, users, categories, items, catalog,
│   │                     # bookings, chat(+WS), wallet, notifications,
│   │                     # reports, admin, router.py
│   ├── models/           # SQLAlchemy: все таблицы ER-диаграммы
│   ├── schemas/          # Pydantic request/response модели
│   ├── services/         # бизнес-логика (booking_service — эталонный пример)
│   └── utils/            # s3, sms (заглушки)
├── alembic/              # миграции
├── tests/                # pytest (sqlite-in-memory фикстуры)
├── docker-compose.yml    # PostgreSQL+PostGIS, Redis, MinIO, API
└── Makefile              # run / migrate / upgrade / test / up

frontend/                 # SPA (Vite + React + TS) — каркас папок
docs/                     # API.md, ARCHITECTURE.md
```

## Быстрый старт
```bash
cd backend
cp .env.example .env
make up                      # инфраструктура (нужен Docker)
pip install -r requirements.txt
make run                     # http://localhost:8000/docs — Swagger UI
make test                    # pytest
```

## Статус каркаса
- Все маршруты зарегистрированы (58 routes), OpenAPI генерируется, тесты проходят.
- Реализован эталонный вертикальный срез: `BookingService` (UC-3→4→5: холд залога,
  approve/reject, confirm-receipt, confirm-return/report-issue).
- Остальные обработчики — заглушки с `NotImplementedError` и TODO-комментариями,
  привязанными к номерам use cases.
