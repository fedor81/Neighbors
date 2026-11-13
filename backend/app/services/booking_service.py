"""Use-case сервис бронирования (UC-3, UC-4, UC-5). Application layer.

Чистая архитектура:
- не импортирует SQLAlchemy и ORM-модели — только порты (domain/ports) и домен;
- не знает про HTTP — бросает доменные исключения (core/exceptions),
  которые presentation-слой мапит в ответы;
- транзакцией управляет UnitOfWork, переданный извне (deps.py).
"""
from decimal import Decimal

from app.core.exceptions import (
    ConflictError, InsufficientFundsError, NotFoundError, PermissionDeniedError,
)
from app.domain.booking_state_machine import ITEM_STATUS_BY_BOOKING, assert_transition
from app.domain.enums import BookingStatus, ItemStatus, NotificationType, TransactionType
from app.domain.ports.repositories import (
    BookingRepository, EventBusPort, ItemRepository, NotificationRepository, WalletRepository,
)


class BookingService:
    def __init__(self, *, uow, bookings: BookingRepository, items: ItemRepository,
                 wallets: WalletRepository, notifications: NotificationRepository,
                 event_bus: EventBusPort):
        self.uow = uow
        self.bookings = bookings
        self.items = items
        self.wallets = wallets
        self.notifications = notifications
        self.event_bus = event_bus

    # ---------- UC-3: создание заявки + холд залога ----------
    def create_booking(self, renter_id: int, item_id: int, start_date, end_date):
        item = self.items.get_for_update(item_id)
        if item is None:
            raise NotFoundError("Вещь не найдена")
        if item.status != ItemStatus.available:
            raise ConflictError("Вещь уже забронирована или занята")
        if item.owner_id == renter_id:
            raise PermissionDeniedError("Нельзя арендовать собственную вещь")

        booking = self.bookings.add(dict(
            item_id=item.id, renter_id=renter_id, status=BookingStatus.pending,
            deposit_held_amount=0, start_date=start_date, end_date=end_date,
        ))

        deposit = Decimal(str(item.deposit_amount or 0))
        if deposit > 0:
            self._hold_deposit(renter_id, deposit, booking)  # при неудаче — откат юнит-работы
            booking.deposit_held_amount = deposit

        item.status = ItemStatus.booked  # «Забронирована» до решения владельца
        self.notifications.add(dict(
            user_id=item.owner_id, type=NotificationType.new_booking,
            message=f"Новая заявка на «{item.title}»",
        ))
        self.event_bus.publish(f"bookings:{booking.id}", {"event": "new_booking"})
        self.uow.commit()
        return booking

    def _hold_deposit(self, renter_id: int, amount: Decimal, booking) -> None:
        """Холд = заморозка, НЕ списание (бизнес-правило UC-3)."""
        wallet = self.wallets.get_for_update(renter_id)
        if wallet is None or Decimal(str(wallet.total_balance)) < amount:
            raise InsufficientFundsError("Недостаточно средств для залога — пополните баланс")
        wallet.total_balance -= amount
        wallet.held_balance += amount
        self.uow.transactions.add(dict(
            user_id=renter_id, booking_id=booking.id, type=TransactionType.hold, amount=amount,
        ))

    # ---------- UC-4: решение владельца ----------
    def approve(self, booking_id: int, owner_id: int):
        booking = self._get_owner_booking(booking_id, owner_id)
        assert_transition(booking.status, BookingStatus.approved)
        booking.status = BookingStatus.approved
        self._notify(booking.renter_id, NotificationType.booking_approved, "Заявка одобрена — договоритесь о встрече в чате")
        self.uow.commit()
        return booking

    def reject(self, booking_id: int, owner_id: int):
        booking = self._get_owner_booking(booking_id, owner_id)
        assert_transition(booking.status, BookingStatus.rejected)
        booking.status = BookingStatus.rejected
        self._release_deposit(booking)
        self._free_item(booking)
        self._notify(booking.renter_id, NotificationType.booking_rejected, "Владелец отклонил заявку, залог разморожен")
        self.uow.commit()
        return booking

    def cancel_by_renter(self, booking_id: int, renter_id: int):
        """Отмена арендатором до встречи (UC-3/UC-4 alt): залог release, рейтинг не трогается."""
        booking = self._get_renter_booking(booking_id, renter_id)
        if booking.status not in (BookingStatus.pending, BookingStatus.approved):
            raise ConflictError("Отмена невозможна на текущей стадии")
        assert_transition(booking.status, BookingStatus.cancelled)
        booking.status = BookingStatus.cancelled
        self._release_deposit(booking)
        self._free_item(booking)
        self.uow.commit()
        return booking

    # ---------- UC-4: старт аренды ----------
    def confirm_receipt(self, booking_id: int, renter_id: int):
        booking = self._get_renter_booking(booking_id, renter_id)
        assert_transition(booking.status, BookingStatus.rented)
        booking.status = BookingStatus.rented
        booking.item.status = ItemStatus.rented
        # TODO: запустить таймер возврата (APScheduler/Celery beat) -> return_reminder
        self.uow.commit()
        return booking

    def refuse_on_inspection(self, booking_id: int, renter_id: int):
        """Отказ при осмотре: сделка аннулируется без влияния на рейтинги (UC-4 alt)."""
        booking = self._get_renter_booking(booking_id, renter_id)
        assert_transition(booking.status, BookingStatus.rejected)
        booking.status = BookingStatus.rejected
        self._release_deposit(booking)
        self._free_item(booking)
        self.uow.commit()
        return booking

    # ---------- UC-5: возврат ----------
    def initiate_return(self, booking_id: int, renter_id: int):
        booking = self._get_renter_booking(booking_id, renter_id)
        if booking.status != BookingStatus.rented:
            raise ConflictError("Возврат возможен только из статуса «в аренде»")
        self._notify(booking.item.owner_id, NotificationType.return_reminder,
                     "Арендатор готов вернуть вещь — договоритесь о встрече")
        self.uow.commit()
        return booking

    def confirm_return(self, booking_id: int, owner_id: int):
        booking = self._get_owner_booking(booking_id, owner_id)
        assert_transition(booking.status, BookingStatus.returned)
        booking.status = BookingStatus.returned
        self._release_deposit(booking)   # разморозка залога
        self._free_item(booking)
        # TODO: открыть окно взаимных оценок (ReviewService, UC-5 шаг 6)
        self.uow.commit()
        return booking

    def report_issue(self, booking_id: int, owner_id: int, reason: str):
        """Порча/проблема -> спор (UC-9): разморозка заблокирована, залог остаётся в held."""
        booking = self._get_owner_booking(booking_id, owner_id)
        assert_transition(booking.status, BookingStatus.disputed)
        booking.status = BookingStatus.disputed
        self.uow.disputes.add(dict(
            kind="booking", booking_id=booking.id, reporter_id=owner_id,
            reported_user_id=booking.renter_id, reason=reason, status="pending",
        ))
        self.uow.commit()
        return booking

    # ---------- вспомогательное ----------
    def _release_deposit(self, booking) -> None:
        amount = Decimal(str(booking.deposit_held_amount or 0))
        if amount <= 0:
            return
        wallet = self.wallets.get_for_update(booking.renter_id)
        wallet.held_balance -= amount
        wallet.total_balance += amount
        self.uow.transactions.add(dict(
            user_id=booking.renter_id, booking_id=booking.id,
            type=TransactionType.release, amount=amount,
        ))

    def _free_item(self, booking) -> None:
        target = ITEM_STATUS_BY_BOOKING[booking.status]
        if target is not None:
            booking.item.status = target
        elif booking.item.status in (ItemStatus.booked, ItemStatus.rented):
            booking.item.status = ItemStatus.available

    def _get_renter_booking(self, booking_id: int, renter_id: int):
        booking = self.bookings.get(booking_id)
        if booking is None or booking.renter_id != renter_id:
            raise NotFoundError("Бронь не найдена")
        return booking

    def _get_owner_booking(self, booking_id: int, owner_id: int):
        booking = self.bookings.get(booking_id)
        if booking is None or booking.item.owner_id != owner_id:
            raise NotFoundError("Бронь не найдена")
        return booking

    def _notify(self, user_id: int, type_: NotificationType, message: str) -> None:
        self.notifications.add(dict(user_id=user_id, type=type_, message=message))
