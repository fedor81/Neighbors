"""Доменные словари (enum'ы). Чистый слой: без SQLAlchemy и Pydantic."""
import enum


class UserRole(str, enum.Enum):
    user = "user"
    moderator = "moderator"


class UserStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"


class ItemStatus(str, enum.Enum):
    available = "available"
    booked = "booked"      # «Забронирована»: заявка создана, ждёт решения владельца
    rented = "rented"
    hidden = "hidden"


class BookingStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    rented = "rented"
    returned = "returned"
    disputed = "disputed"
    cancelled = "cancelled"


class TransactionType(str, enum.Enum):
    deposit = "deposit"      # пополнение баланса (учебная заглушка)
    withdrawal = "withdrawal"
    hold = "hold"            # заморозка залога (НЕ списание)
    release = "release"      # разморозка
    charge = "charge"        # списание в пользу владельца по решению модератора


class DisputeKind(str, enum.Enum):
    booking = "booking"      # спор по заказу (UC-9)
    content = "content"      # жалоба на объявление/сообщение/пользователя (UC-10)


class DisputeStatus(str, enum.Enum):
    pending = "pending"
    resolved = "resolved"
    dismissed = "dismissed"


class ReportTarget(str, enum.Enum):
    item = "item"
    message = "message"
    user = "user"


class NotificationType(str, enum.Enum):
    new_booking = "new_booking"
    booking_approved = "booking_approved"
    booking_rejected = "booking_rejected"
    message = "message"
    return_reminder = "return_reminder"
    dispute_update = "dispute_update"


class RentalFormat(str, enum.Enum):
    free = "free"
    barter = "barter"
    money = "money"
