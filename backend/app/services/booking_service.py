"""Сервис бронирования (UC-3, UC-4, UC-5). Каркас бизнес-логики.

Жизненный цикл заказа:
pending -> approved/rejected -> rented -> returned/disputed/cancelled
"""
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Booking, BookingStatus, Item, ItemStatus, TransactionType, User, Wallet, WalletTransaction


class BookingService:
    def __init__(self, db: Session):
        self.db = db

    # ---------- UC-3: создание заявки + холд залога ----------
    def create_booking(self, renter: User, item_id: int, start_date, end_date) -> Booking:
        item = self.db.get(Item, item_id)
        if not item or item.status != ItemStatus.available:
            raise HTTPException(404, detail="Item not found or unavailable")
        if item.owner_id == renter.id:
            raise HTTPException(400, detail="Cannot rent own item")

        booking = Booking(
            item_id=item.id,
            renter_id=renter.id,
            status=BookingStatus.pending,
            deposit_held_amount=0,
            start_date=start_date,
            end_date=end_date,
        )
        self.db.add(booking)
        self.db.flush()  # получаем booking.id до холда

        if item.deposit_amount and item.deposit_amount > 0:
            self._hold_deposit(renter, item.deposit_amount, booking)
            booking.deposit_held_amount = item.deposit_amount

        item.status = ItemStatus.booked  # вещь недоступна другим, пока заявка висит
        self.db.commit()
        self.db.refresh(booking)
        # TODO: уведомление владельцу (NotificationService)
        return booking

    def _hold_deposit(self, renter: User, amount: Decimal, booking: Booking) -> None:
        wallet = self.db.query(Wallet).filter(Wallet.user_id == renter.id).with_for_update().first()
        if wallet is None or wallet.total_balance < amount:
            raise HTTPException(400, detail={"code": "INSUFFICIENT_FUNDS",
                                             "message": "Недостаточно средств для залога"})
        wallet.total_balance -= amount
        wallet.held_balance += amount
        self.db.add(WalletTransaction(user_id=renter.id, booking_id=booking.id,
                                      type=TransactionType.hold, amount=amount))

    # ---------- UC-4: решение владельца ----------
    def approve(self, booking_id: int, owner_id: int) -> Booking:
        booking = self._get_owner_booking(booking_id, owner_id)
        booking.status = BookingStatus.approved
        self.db.commit()
        # TODO: создать чат-комнату, уведомить арендатора
        return booking

    def reject(self, booking_id: int, owner_id: int) -> Booking:
        booking = self._get_owner_booking(booking_id, owner_id)
        booking.status = BookingStatus.rejected
        self._release_or_refund(booking, to_owner=False)
        booking.item.status = ItemStatus.available
        self.db.commit()
        return booking

    # ---------- UC-4: старт аренды ----------
    def confirm_receipt(self, booking_id: int, renter_id: int) -> Booking:
        booking = self._get_renter_booking(booking_id, renter_id)
        if booking.status != BookingStatus.approved:
            raise HTTPException(400, detail="Booking is not approved")
        booking.status = BookingStatus.rented
        booking.item.status = ItemStatus.rented
        self.db.commit()
        # TODO: запустить таймер аренды (celery beat / apscheduler)
        return booking

    # ---------- UC-5: возврат ----------
    def confirm_return(self, booking_id: int, owner_id: int) -> Booking:
        booking = self._get_owner_booking(booking_id, owner_id)
        if booking.status != BookingStatus.rented:
            raise HTTPException(400, detail="Booking is not in rented state")
        booking.status = BookingStatus.returned
        booking.item.status = ItemStatus.available
        self._release_or_refund(booking, to_owner=False)  # разморозка залога
        self.db.commit()
        # TODO: открыть окно взаимных оценок
        return booking

    def report_issue(self, booking_id: int, owner_id: int, reason: str) -> Booking:
        """Порча/проблема -> спор, разморозка заблокирована, подключается модератор (UC-9)."""
        booking = self._get_owner_booking(booking_id, owner_id)
        booking.status = BookingStatus.disputed
        self.db.commit()
        # TODO: создать Dispute(reason), уведомить модератора
        return booking

    # ---------- вспомогательное ----------
    def _release_or_refund(self, booking: Booking, to_owner: bool) -> None:
        if booking.deposit_held_amount <= 0:
            return
        renter_wallet = self.db.query(Wallet).filter(Wallet.user_id == booking.renter_id).first()
        if to_owner:  # списание в пользу владельца (решение модератора)
            renter_wallet.held_balance -= booking.deposit_held_amount
            owner_wallet = self.db.query(Wallet).filter(
                Wallet.user_id == booking.item.owner_id).first()
            owner_wallet.total_balance += booking.deposit_held_amount
            ttype = TransactionType.charge
        else:  # обычная разморозка
            renter_wallet.held_balance -= booking.deposit_held_amount
            renter_wallet.total_balance += booking.deposit_held_amount
            ttype = TransactionType.release
        self.db.add(WalletTransaction(user_id=booking.renter_id, booking_id=booking.id,
                                      type=ttype, amount=booking.deposit_held_amount))

    def _get_renter_booking(self, booking_id: int, renter_id: int) -> Booking:
        booking = self.db.get(Booking, booking_id)
        if not booking or booking.renter_id != renter_id:
            raise HTTPException(404, detail="Booking not found")
        return booking

    def _get_owner_booking(self, booking_id: int, owner_id: int) -> Booking:
        booking = self.db.get(Booking, booking_id)
        if not booking or booking.item.owner_id != owner_id:
            raise HTTPException(404, detail="Booking not found")
        return booking
