# REST API v1 — карта эндпоинтов

Базовый URL: `/api/v1`. Auth: `Authorization: Bearer <access_token>`.
Ошибки: `{ "error": { "code": "...", "message": "..." } }`.

| Группа | Эндпоинты | UC |
|---|---|---|
| auth | POST /auth/phone/send-code, /auth/phone/verify, /auth/refresh, /auth/logout | UC-1 |
| users | GET/PATCH /users/me, PUT /users/me/location, GET /users/me/history, GET /users/{id}/public | UC-2, UC-7 |
| categories | GET /categories, GET /categories/{slug} | — |
| items | POST /items, GET /items/{id}, /items/me, PATCH, DELETE, POST hide/show, POST/DELETE photos | UC-6 |
| catalog | GET /catalog?category_id&q&radius_km&mode=local\|city&availability&cursor | UC-3 |
| bookings | POST /bookings (атомарный холд), GET /bookings/me, GET/{id}; approve, reject, cancel, confirm-receipt, refuse-on-inspection, initiate-return, confirm-return, report-issue; POST/GET reviews | UC-3..5 |
| chat | GET/POST /bookings/{id}/messages, POST .../read, GET /chats/unread-count, WS /ws/bookings/{id}/chat | UC-4 |
| wallet | GET /wallet, POST /wallet/top-up (заглушка), GET /wallet/transactions | UC-7 |
| notifications | GET /notifications, POST /notifications/read, GET/PUT settings | UC-8 |
| reports | POST /reports, GET /reports/me | UC-10 |
| admin | GET /admin/disputes[/{id}], POST resolve; /admin/reports[/{id}/resolve]; /admin/users/{id}/ban/unban; /admin/categories | UC-9, UC-10 |

Полные схемы запросов/ответов — в Swagger UI (`/docs`) после запуска;
Pydantic-модели: `app/schemas/schemas.py`.
