# Архитектура (MVP)

## Стек
| Слой | Выбор | Обоснование |
|---|---|---|
| API | Python 3.12 + FastAPI | автогенерация OpenAPI, WebSocket из коробки |
| БД | PostgreSQL 16 + PostGIS | гео-выдача «шаговой доступности» (ST_DWithin) |
| ORM | SQLAlchemy 2.0 + Alembic | typed models, миграции |
| Кэш/коды/RT | Redis | SMS-коды с TTL, rate-limit, pub/sub для WS-чата |
| Файлы | S3-совместимый (MinIO локально) | фото вещей; загрузка через бэкенд (валидация/сжатие) |
| Auth | JWT access(15м)+refresh(30д) | верификация только по телефону (решение N-1) |
| Frontend | Vite + React + TypeScript | адаптивный веб (решение N-4: не приложение) |

## Ключевые доменные инварианты
1. **Залог** — холдирование на виртуальном балансе, не списание. Запрос владельцу
   не уходит без успешного холда (если залог > 0).
2. **Статус вещи** меняется атомарно со статусом заказа: pending/approved → booked,
   rented → rented, returned/rejected/cancelled → available.
3. **Спор (disputed)**: разморозка заблокирована, выход только решением модератора.
4. **Приватность**: телефон не раскрывается (чат привязан к booking), адрес
   владельца не раскрывается (в выдаче только distance_m).
5. **Оценки** публикуются после встречной оценки или истечения срока (is_visible).
6. **Выдача**: mode=local от точки пользователя; пустая локальная → fallback city;
   точка не верифицируется.

## Машина состояний Booking
```
pending ──approve──> approved ──confirm-receipt──> rented ──confirm-return──> returned
   │                     │                            │
   ├─reject/ttl──> rejected                           ├─report-issue/просрочка──> disputed
   ├─cancel──> cancelled                              └─refuse-on-inspection──> cancelled
   └─(залог release)                                  disputed ──resolve──> returned|cancelled
```

## Что осталось реализовать (порядок)
1. UC-1 auth: Redis-коды, upsert user+wallet, токены.
2. UC-2/7: location, профиль, history.
3. UC-6: items CRUD + загрузка фото в MinIO.
4. UC-3: catalog с PostGIS-радиусом + курсорная пагинация.
5. UC-4/5: чат (REST+WS), reviews с is_visible.
6. UC-8: notifications (лента + email-заглушка).
7. UC-9/10: админка модератора.
8. Фронтенд: страницы Login/Catalog/ItemCard/Bookings/Chat/Profile/Admin.
