"""Use-case сервис объявлений (UC-6). Application layer, без ORM и HTTP."""
from decimal import Decimal

from app.core.exceptions import ConflictError, NotFoundError, PermissionDeniedError, ProhibitedItemError
from app.domain.enums import ItemStatus
from app.domain.ports.repositories import BookingRepository, CategoryRepository, ItemRepository
from app.domain.prohibited import contains_prohibited


class ItemService:
    def __init__(self, *, uow, items: ItemRepository, bookings: BookingRepository,
                 categories: CategoryRepository):
        self.uow = uow
        self.items = items
        self.bookings = bookings
        self.categories = categories

    # ---------- UC-6: публикация ----------
    def create_item(self, owner_id: int, *, title: str, description: str | None,
                    category_id: int, deposit_amount: Decimal, rental_format: str):
        if contains_prohibited(title) or contains_prohibited(description):
            raise ProhibitedItemError(
                "Размещаются только физические предметы; услуги, еда и медикаменты запрещены")
        if self.categories.get(category_id) is None:
            raise NotFoundError("Категория не найдена")

        item = self.items.add(dict(
            owner_id=owner_id, category_id=category_id, title=title,
            description=description, deposit_amount=deposit_amount,
            format=rental_format, status=ItemStatus.available,
        ))
        self.uow.commit()
        return item

    def update_item(self, item_id: int, user_id: int, **fields):
        item = self._get_owned(item_id, user_id)
        if item.status in (ItemStatus.booked, ItemStatus.rented):
            raise ConflictError("Нельзя редактировать вещь во время активной аренды")
        for key, value in fields.items():
            if value is not None and hasattr(item, key):
                setattr(item, key, value)
        self.uow.commit()
        return item

    # ---------- скрытие/возврат в выдачу ----------
    def hide(self, item_id: int, user_id: int):
        """'Недоступна': исчезает из выдачи, активные заказы продолжают выполняться (UC-6 alt)."""
        item = self._get_owned(item_id, user_id)
        item.status = ItemStatus.hidden
        self.uow.commit()
        return item

    def show(self, item_id: int, user_id: int):
        item = self._get_owned(item_id, user_id)
        if item.status != ItemStatus.hidden:
            raise ConflictError("Вещь уже в выдаче")
        item.status = ItemStatus.available
        self.uow.commit()
        return item

    def delete(self, item_id: int, user_id: int) -> None:
        item = self._get_owned(item_id, user_id)
        active = [b for b in item.bookings
                  if b.status.value in ("pending", "approved", "rented", "disputed")]
        if active:
            raise ConflictError("Есть активные брони — удаление запрещено")
        # TODO: удалить объекты фото из S3 через FileStoragePort.delete(storage_key)
        self.items.delete(item)
        self.uow.commit()

    def _get_owned(self, item_id: int, user_id: int):
        item = self.items.get(item_id)
        if item is None:
            raise NotFoundError("Вещь не найдена")
        if item.owner_id != user_id:
            raise PermissionDeniedError("Изменять объявления может только владелец")
        return item
