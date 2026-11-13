"""Use-case витрины каталога (UC-3 шаги 1-2).

Логика выдачи:
- mode=local: вещи в радиусе DEFAULT_LOCAL_RADIUS_KM от точки пользователя;
- локальная выдача пуста -> fallback на mode=city с явным флагом в meta;
- без точки проживания доступен только city.
В выдаче показывается distance_m; адрес владельца не раскрывается (решение N-2).
"""
import math

from app.core.config import settings
from app.domain.ports.repositories import ItemRepository


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> int:
    """Расстояние между точками, метры (упрощённая сферическая модель)."""
    r = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return int(round(2 * r * math.asin(math.sqrt(a))))


class CatalogService:
    def __init__(self, *, items: ItemRepository):
        self.items = items

    def search(self, user, *, category_id=None, q=None, radius_km=None, mode="local",
               availability=None, cursor=None, limit=20):
        limit = max(1, min(limit, 50))
        has_location = user.latitude is not None and user.longitude is not None
        radius = radius_km or settings.DEFAULT_LOCAL_RADIUS_KM

        # Без точки проживания local недоступен — сразу город (бизнес-правило UC-3 alt).
        if not has_location:
            mode = "city"

        rows, next_cursor = self.items.search(
            lat=user.latitude, lon=user.longitude, radius_km=radius, mode=mode,
            category_id=category_id, q=q, availability=availability,
            cursor=cursor, limit=limit,
        )

        results = []
        for item, distance in rows:
            if distance is None and has_location and item.owner.latitude is not None:
                distance = haversine_m(float(user.latitude), float(user.longitude),
                                       float(item.owner.latitude), float(item.owner.longitude))
            if mode == "local" and distance is not None and distance > radius * 1000:
                continue  # TODO(prod): фильтрацию радиуса делает PostGIS ST_DWithin
            results.append((item, distance))

        fallback = False
        if mode == "local" and not results and not cursor:
            # Локальная выдача пуста -> расширяем до города, помечаем в meta (решение N-4).
            rows, next_cursor = self.items.search(
                lat=user.latitude, lon=user.longitude, radius_km=radius, mode="city",
                category_id=category_id, q=q, availability=availability,
                cursor=None, limit=limit,
            )
            results = [(it, d) for it, d in rows]
            fallback = True

        return {"items": results, "meta": {"mode": mode if not fallback else "city",
                                           "fallback_from_local": fallback,
                                           "next_cursor": next_cursor}}
