"""Unit of Work: одна транзакция БД на use-case + фабрики репозиториев.

Сервисы вызывают uow.commit()/rollback(); вне UoW они не знают ни сессий, ни ORM.
"""
from sqlalchemy.orm import Session

from app.persistence import models as m
from app.persistence.api.repositories.sqlalchemy_repositories import (
    SqlBookingRepository, SqlCategoryRepository, SqlDisputeRepository, SqlItemRepository,
    SqlMessageRepository, SqlNotificationRepository, SqlReviewRepository,
    SqlTransactionRepository, SqlUserRepository, SqlWalletRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session):
        self.session = session
        # Репозитории (порты -> адаптеры)
        self.users = SqlUserRepository(session)
        self.wallets = SqlWalletRepository(session)
        self.items = SqlItemRepository(session)
        self.bookings = SqlBookingRepository(session)
        self.categories = SqlCategoryRepository(session)
        self.messages = SqlMessageRepository(session)
        self.reviews = SqlReviewRepository(session)
        self.transactions = SqlTransactionRepository(session)
        self.disputes = SqlDisputeRepository(session)
        self.notifications = SqlNotificationRepository(session)

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close(self):
        self.session.close()

    # convenience-фабрики для записи служебных сущностей внутри use-case
    class _ModelAdder:
        def __init__(self, session: Session, model):
            self.session, self.model = session, model

        def add(self, kwargs: dict):
            entity = self.model(**kwargs)
            self.session.add(entity)
            self.session.flush()
            return entity

    @property
    def tx_adder(self):  # совместимость: сервисы пишут через конкретные репозитории
        return self._ModelAdder(self.session, m.WalletTransaction)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type:
            self.rollback()
        self.close()
