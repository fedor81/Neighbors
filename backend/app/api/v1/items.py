"""Items endpoints (UC-6): публикация и управление объявлениями."""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas import ItemCreate, ItemOut

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemOut, status_code=201)
def create_item(data: ItemCreate, user: User = Depends(get_current_user)):
    """Только физические предметы; услуги/еда/медикаменты запрещены (стоп-слова + модерация)."""
    raise NotImplementedError


@router.get("/me")
def my_items(user: User = Depends(get_current_user), status: str | None = None):
    raise NotImplementedError


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, user: User = Depends(get_current_user)):
    """Карточка: фото, описание, залог, рейтинг владельца, расстояние (не адрес)."""
    raise NotImplementedError


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.post("/{item_id}/hide")
def hide_item(item_id: int, user: User = Depends(get_current_user)):
    """Скрытие из выдачи; активные заказы продолжают выполняться."""
    raise NotImplementedError


@router.post("/{item_id}/show")
def show_item(item_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.delete("/{item_id}", status_code=204)
def delete_item(item_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.post("/{item_id}/photos")
def upload_photo(item_id: int, user: User = Depends(get_current_user)):
    """multipart-загрузка через бэкенд -> S3/MinIO (валидация размера/типа, сжатие)."""
    raise NotImplementedError


@router.delete("/{item_id}/photos/{photo_id}", status_code=204)
def delete_photo(item_id: int, photo_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError
