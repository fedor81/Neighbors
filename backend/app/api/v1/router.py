"""Главный роутер v1: собирает все модули."""
from fastapi import APIRouter

from app.api.v1 import (
    admin, auth, bookings, catalog, categories, chat,
    items, notifications, reports, users, wallet,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(items.router)
api_router.include_router(catalog.router)
api_router.include_router(bookings.router)
api_router.include_router(chat.router)
api_router.include_router(wallet.router)
api_router.include_router(notifications.router)
api_router.include_router(reports.router)
api_router.include_router(admin.router)
