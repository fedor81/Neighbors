"""Реализации портов репозиториев на SQLAlchemy (adapter-слой).

Репозитории — единственное место, где services-слой соприкасается с ORM.
Порты объявлены в app/domain/ports/repositories.py.
"""
from typing import Iterable

from sqlalchemy import func as sa_func, or_, select, update
from sqlalchemy.orm import Session

from app.domain.enums import ItemStatus
from app.domain.ports.repositories import (
    BookingRepository, CategoryRepository, DisputeRepository, ItemRepository,
    MessageRepository, NotificationRepository, ReviewRepository, TransactionRepository,
    UserRepository, WalletRepository,
)
from app.persistence import models as m


class BaseSqlRepo:
    model = None  # тип subclass

    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id: int):
        return self.db.get(self.model, entity_id)

    def add(self, entity):
        self.db.add(entity)
        self.db.flush()
        return entity

    def delete(self, entity):
        self.db.delete(entity)
        self.db.flush()


class SqlUserRepository(BaseSqlRepo, UserRepository):
    model = m.User

    def get_by_phone(self, phone: str):
        return self.db.scalar(select(m.User).where(m.User.phone == phone))

    def list_active(self, offset: int = 0, limit: int = 50):
        stmt = (select(m.User).where(m.User.status == m.UserStatus.active)
                .offset(offset).limit(limit))
        return list(self.db.scalars(stmt))


class SqlWalletRepository(BaseSqlRepo, WalletRepository):
    model = m.Wallet

    def get_for_update(self, user_id: int):
        stmt = select(m.Wallet).where(m.Wallet.user_id == user_id).with_for_update()
        return self.db.scalar(stmt)

    def get_by_user(self, user_id: int):
        return self.db.scalar(select(m.Wallet).where(m.Wallet.user_id == user_id))


def _decode_cursor(cursor: str | None) -> int:
    """Курсор — id последней видимой записи (keyset-пагинация)."""
    try:
        return int(cursor) if cursor else 0
    except (TypeError, ValueError):
        return 0


class SqlItemRepository(BaseSqlRepo, ItemRepository):
    model = m.Item

    def get_for_update(self, item_id: int):
        stmt = select(m.Item).where(m.Item.id == item_id).with_for_update()
        return self.db.scalar(stmt)

    def list_by_owner(self, owner_id: int, status: str | None = None):
        stmt = select(m.Item).where(m.Item.owner_id == owner_id)
        if status:
            stmt = stmt.where(m.Item.status == ItemStatus(status))
        return list(self.db.scalars(stmt.order_by(m.Item.created_at.desc())))

    def search(self, *, lat, lon, radius_km, mode, category_id, q,
               availability, cursor, limit):
        """Витрина UC-3.

        TODO(prod): заменить на PostGIS ST_DWithin + ST_Distance; здесь — каркас:
        фильтрация по категории/поиску/доступности + keyset-пагинация, расстояние
        считается приложением (haversine) для режима local.
        """
        stmt = select(m.Item).where(m.Item.status != ItemStatus.hidden)
        if category_id:
            stmt = stmt.where(m.Item.category_id == category_id)
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(or_(sa_func.lower(m.Item.title).like(like),
                                  sa_func.lower(m.Item.description).like(like)))
        if availability == "available":
            stmt = stmt.where(m.Item.status == ItemStatus.available)
        elif availability == "busy":
            stmt = stmt.where(m.Item.status.in_([ItemStatus.booked, ItemStatus.rented]))
        last_id = _decode_cursor(cursor)
        if last_id:
            stmt = stmt.where(m.Item.id < last_id)
        stmt = stmt.order_by(m.Item.id.desc()).limit(limit + 1)
        rows = list(self.db.scalars(stmt))
        next_cursor = str(rows[limit - 1].id) if len(rows) > limit else None
        items = [(it, None) for it in rows[:limit]]  # (item, distance_m) — distance считает GeoService
        return items, next_cursor


class SqlBookingRepository(BaseSqlRepo, BookingRepository):
    model = m.Booking

    def _list(self, column, user_id: int, status: str | None):
        stmt = select(m.Booking).where(column == user_id)
        if status:
            from app.domain.enums import BookingStatus
            stmt = stmt.where(m.Booking.status == BookingStatus(status))
        return list(self.db.scalars(stmt.order_by(m.Booking.created_at.desc())))

    def list_for_renter(self, renter_id: int, status: str | None):
        return self._list(m.Booking.renter_id, renter_id, status)

    def list_for_owner(self, owner_id: int, status: str | None):
        stmt = (select(m.Booking).join(m.Item, m.Booking.item_id == m.Item.id)
                .where(m.Item.owner_id == owner_id))
        if status:
            from app.domain.enums import BookingStatus
            stmt = stmt.where(m.Booking.status == BookingStatus(status))
        return list(self.db.scalars(stmt.order_by(m.Booking.created_at.desc())))


class SqlCategoryRepository(BaseSqlRepo, CategoryRepository):
    model = m.Category

    def list_active(self):
        stmt = (select(m.Category).where(m.Category.is_active.is_(True))
                .order_by(m.Category.sort_order))
        return list(self.db.scalars(stmt))

    def get_by_slug(self, slug: str):
        return self.db.scalar(select(m.Category).where(m.Category.slug == slug))


class SqlMessageRepository(BaseSqlRepo, MessageRepository):
    model = m.Message

    def list_by_booking(self, booking_id: int, cursor: str | None, limit: int):
        stmt = select(m.Message).where(m.Message.booking_id == booking_id)
        last_id = _decode_cursor(cursor)
        if last_id:
            stmt = stmt.where(m.Message.id > last_id)
        stmt = stmt.order_by(m.Message.id).limit(limit + 1)
        rows = list(self.db.scalars(stmt))
        next_cursor = str(rows[limit - 1].id) if len(rows) > limit else None
        return rows[:limit], next_cursor

    def mark_read_until(self, booking_id: int, user_id: int, until_message_id: int) -> int:
        stmt = (update(m.Message)
                .where(m.Message.booking_id == booking_id,
                       m.Message.sender_id != user_id,
                       m.Message.id <= until_message_id,
                       m.Message.is_read.is_(False))
                .values(is_read=True))
        return self.db.execute(stmt).rowcount or 0

    def unread_count(self, user_id: int) -> int:
        stmt = (select(sa_func.count(m.Message.id))
                .join(m.Booking, m.Message.booking_id == m.Booking.id)
                .join(m.Item, m.Booking.item_id == m.Item.id)
                .where(or_(m.Booking.renter_id == user_id, m.Item.owner_id == user_id),
                       m.Message.sender_id != user_id,
                       m.Message.is_read.is_(False)))
        return self.db.scalar(stmt) or 0


class SqlReviewRepository(BaseSqlRepo, ReviewRepository):
    model = m.Review

    def list_for_booking(self, booking_id: int):
        return list(self.db.scalars(select(m.Review).where(m.Review.booking_id == booking_id)))

    def list_visible_for_user(self, user_id: int, cursor: str | None, limit: int):
        stmt = select(m.Review).where(m.Review.reviewee_id == user_id, m.Review.is_visible.is_(True))
        last_id = _decode_cursor(cursor)
        if last_id:
            stmt = stmt.where(m.Review.id < last_id)
        stmt = stmt.order_by(m.Review.id.desc()).limit(limit + 1)
        rows = list(self.db.scalars(stmt))
        next_cursor = str(rows[limit - 1].id) if len(rows) > limit else None
        return rows[:limit], next_cursor

    def rating_summary(self, user_id: int):
        stmt = (select(sa_func.avg(m.Review.rating), sa_func.count(m.Review.rating))
                .where(m.Review.reviewee_id == user_id, m.Review.is_visible.is_(True)))
        avg, cnt = self.db.execute(stmt).one()
        return (round(float(avg), 2) if avg is not None else None), int(cnt or 0)


class SqlTransactionRepository(BaseSqlRepo, TransactionRepository):
    model = m.WalletTransaction

    def list_by_user(self, user_id: int, type_: str | None, cursor: str | None, limit: int):
        from app.domain.enums import TransactionType
        stmt = select(m.WalletTransaction).where(m.WalletTransaction.user_id == user_id)
        if type_:
            stmt = stmt.where(m.WalletTransaction.type == TransactionType(type_))
        last_id = _decode_cursor(cursor)
        if last_id:
            stmt = stmt.where(m.WalletTransaction.id < last_id)
        stmt = stmt.order_by(m.WalletTransaction.id.desc()).limit(limit + 1)
        rows = list(self.db.scalars(stmt))
        next_cursor = str(rows[limit - 1].id) if len(rows) > limit else None
        return rows[:limit], next_cursor


class SqlDisputeRepository(BaseSqlRepo, DisputeRepository):
    model = m.Dispute

    def list_by_status(self, status: str) -> Iterable:
        stmt = select(m.Dispute).where(m.Dispute.status == status).order_by(m.Dispute.created_at)
        return list(self.db.scalars(stmt))


class SqlNotificationRepository(BaseSqlRepo, NotificationRepository):
    model = m.Notification

    def list_by_user(self, user_id: int, cursor: str | None, limit: int):
        stmt = select(m.Notification).where(m.Notification.user_id == user_id)
        last_id = _decode_cursor(cursor)
        if last_id:
            stmt = stmt.where(m.Notification.id < last_id)
        stmt = stmt.order_by(m.Notification.id.desc()).limit(limit + 1)
        rows = list(self.db.scalars(stmt))
        next_cursor = str(rows[limit - 1].id) if len(rows) > limit else None
        return rows[:limit], next_cursor

    def mark_read(self, user_id: int, ids: list[int] | None, all_: bool) -> int:
        stmt = update(m.Notification).where(m.Notification.user_id == user_id,
                                            m.Notification.is_read.is_(False))
        if not all_:
            stmt = stmt.where(m.Notification.id.in_(ids or []))
        return self.db.execute(stmt.values(is_read=True)).rowcount or 0


SQL_REPOSITORIES = {
    UserRepository: SqlUserRepository,
    WalletRepository: SqlWalletRepository,
    ItemRepository: SqlItemRepository,
    BookingRepository: SqlBookingRepository,
    CategoryRepository: SqlCategoryRepository,
    MessageRepository: SqlMessageRepository,
    ReviewRepository: SqlReviewRepository,
    TransactionRepository: SqlTransactionRepository,
    DisputeRepository: SqlDisputeRepository,
    NotificationRepository: SqlNotificationRepository,
}
