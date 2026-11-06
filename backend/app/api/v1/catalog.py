"""Catalog / search endpoint (UC-3).

Логика выдачи:
- mode=local (по умолчанию): вещи в радиусе шаговой доступности от точки пользователя;
- локальная выдача пуста -> fallback на mode=city с явным флагом в meta;
- без точки проживания доступен только city.
В выдаче показывается distance_m, адрес владельца не раскрывается.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("")
def search_catalog(
    user: User = Depends(get_current_user),
    category_id: int | None = None,
    q: str | None = None,
    radius_km: float | None = None,
    mode: str = "local",  # local | city
    availability: str | None = None,  # available | busy
    cursor: str | None = None,
    limit: int = 20,
):
    raise NotImplementedError  # TODO: PostGIS-задача ST_DWithin + курсорная пагинация
