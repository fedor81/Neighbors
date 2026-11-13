"""Чистые доменные правила машины состояний Booking (UC-3..UC-5).

Слой domain не знает про БД/FastAPI — только правила перехода статусов.
"""
from app.core.exceptions import InvalidStateTransitionError
from app.domain.enums import BookingStatus, ItemStatus

# Разрешённые переходы статусов заказа (см. docs/ARCHITECTURE.md).
BOOKING_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.pending: {
        BookingStatus.approved,   # владелец одобрил (UC-4)
        BookingStatus.rejected,   # владелец отклонил / таймаут ответа (UC-4)
        BookingStatus.cancelled,  # арендатор отменил до ответа (UC-3)
    },
    BookingStatus.approved: {
        BookingStatus.rented,     # подтверждение получения на встрече (UC-4)
        BookingStatus.cancelled,  # отмена после одобрения, до встречи (UC-4)
        BookingStatus.rejected,   # отказ при осмотре (UC-4)
    },
    BookingStatus.rented: {
        BookingStatus.returned,   # возврат без повреждений (UC-5)
        BookingStatus.disputed,   # порча / просрочка возврата (UC-5 -> UC-9)
    },
    BookingStatus.disputed: {
        # Из спора заказ выводит ТОЛЬКО модератор (UC-9).
        BookingStatus.returned,   # refund: залог разморожен, сделка закрыта
        BookingStatus.cancelled,  # dismiss жалобы
    },
    BookingStatus.returned: set(),
    BookingStatus.rejected: set(),
    BookingStatus.cancelled: set(),
}

# Статус вещи, соответствующий активным статусам брони (инвариант витрины).
ITEM_STATUS_BY_BOOKING: dict[BookingStatus, ItemStatus | None] = {
    BookingStatus.pending: ItemStatus.booked,
    BookingStatus.approved: ItemStatus.booked,
    BookingStatus.rented: ItemStatus.rented,
    BookingStatus.returned: None,   # доступность решает ItemService (hidden vs available)
    BookingStatus.rejected: None,
    BookingStatus.cancelled: None,
    BookingStatus.disputed: ItemStatus.rented,  # вещь у арендатора до решения модератора
}


def assert_transition(current: BookingStatus, target: BookingStatus) -> None:
    if target not in BOOKING_TRANSITIONS[current]:
        raise InvalidStateTransitionError(
            f"Переход брони {current.value} -> {target.value} запрещён"
        )
