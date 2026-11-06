"""Точка входа FastAPI. Сервис обмена вещами между соседями."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="Neighbors — обмен вещами между соседями",
    version="0.1.0",
    description="MVP: каталог вещей ЖК, бронирование с залогом, чат, рейтинги, модерация.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}
