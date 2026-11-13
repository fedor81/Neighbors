"""Порты (абстракции) для репозиториев и внешних сервисов.

Чистая архитектура: services-слой зависит только от этих ABC.
Реализации — в app/persistence (SQLAlchemy) и app/infrastructure (Redis, S3, SMS).
"""
from abc import ABC, abstractmethod
from typing import Any, Generic, Iterable, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Базовый CRUD-порт."""

    @abstractmethod
    def get(self, entity_id: int) -> T | None: ...

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, entity: T) -> None: ...


class UserRepository(Repository, ABC):
    @abstractmethod
    def get_by_phone(self, phone: str) -> Any | None: ...

    @abstractmethod
    def list_active(self, offset: int = 0, limit: int = 50) -> Iterable: ...


class WalletRepository(Repository, ABC):
    @abstractmethod
    def get_for_update(self, user_id: int) -> Any | None:
        """SELECT ... FOR UPDATE — блокировка строки для атомарного холда."""

    @abstractmethod
    def get_by_user(self, user_id: int) -> Any | None: ...


class ItemRepository(Repository, ABC):
    @abstractmethod
    def get_for_update(self, item_id: int) -> Any | None: ...

    @abstractmethod
    def list_by_owner(self, owner_id: int, status: str | None = None) -> Iterable: ...

    @abstractmethod
    def search(self, *, lat: float | None, lon: float | None, radius_km: float,
               mode: str, category_id: int | None, q: str | None,
               availability: str | None, cursor: str | None, limit: int) -> tuple[list, str | None]:
        """Витрина UC-3: local/city выдача, курсорная пагинация.
        Возвращает (rows, next_cursor). rows — кортежи (item, distance_m)."""


class BookingRepository(Repository, ABC):
    @abstractmethod
    def list_for_renter(self, renter_id: int, status: str | None) -> Iterable: ...

    @abstractmethod
    def list_for_owner(self, owner_id: int, status: str | None) -> Iterable: ...


class CategoryRepository(Repository, ABC):
    @abstractmethod
    def list_active(self) -> Iterable: ...

    @abstractmethod
    def get_by_slug(self, slug: str) -> Any | None: ...


class MessageRepository(Repository, ABC):
    @abstractmethod
    def list_by_booking(self, booking_id: int, cursor: str | None, limit: int) -> tuple[list, str | None]: ...

    @abstractmethod
    def mark_read_until(self, booking_id: int, user_id: int, until_message_id: int) -> int: ...

    @abstractmethod
    def unread_count(self, user_id: int) -> int: ...


class ReviewRepository(Repository, ABC):
    @abstractmethod
    def list_for_booking(self, booking_id: int) -> Iterable: ...

    @abstractmethod
    def list_visible_for_user(self, user_id: int, cursor: str | None, limit: int) -> tuple[list, str | None]: ...

    @abstractmethod
    def rating_summary(self, user_id: int) -> tuple[float | None, int]:
        """(средний рейтинг, число оценок) по опубликованным отзывам."""


class TransactionRepository(Repository, ABC):
    @abstractmethod
    def list_by_user(self, user_id: int, type_: str | None, cursor: str | None, limit: int) -> tuple[list, str | None]: ...


class DisputeRepository(Repository, ABC):
    @abstractmethod
    def list_by_status(self, status: str) -> Iterable: ...


class NotificationRepository(Repository, ABC):
    @abstractmethod
    def list_by_user(self, user_id: int, cursor: str | None, limit: int) -> tuple[list, str | None]: ...

    @abstractmethod
    def mark_read(self, user_id: int, ids: list[int] | None, all_: bool) -> int: ...


# ---------------- внешние порты (adapters в infrastructure/) ----------------

class SmsSenderPort(ABC):
    @abstractmethod
    def send(self, phone: str, text: str) -> None: ...


class CodeStoragePort(ABC):
    """Хранилище одноразовых SMS-кодов (Redis: sms:code:<phone>, TTL + попытки)."""

    @abstractmethod
    def save(self, phone: str, code: str, ttl_seconds: int) -> None: ...

    @abstractmethod
    def check_and_consume(self, phone: str, code: str, max_attempts: int) -> bool: ...

    @abstractmethod
    def can_resend(self, phone: str, cooldown_seconds: int) -> bool: ...


class FileStoragePort(ABC):
    @abstractmethod
    def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Возвращает публичный URL объекта."""

    @abstractmethod
    def delete(self, key: str) -> None: ...


class EventBusPort(ABC):
    """Pub/Sub для real-time (WS-чат, push уведомлений). Redis Pub/Sub в проде."""

    @abstractmethod
    def publish(self, channel: str, payload: dict[str, Any]) -> None: ...
