"""Profile & location endpoints (UC-2, UC-7)."""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas import UserProfile, UserUpdate, LocationUpdate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
def get_me(user: User = Depends(get_current_user)):
    raise NotImplementedError  # каркас


@router.patch("/me", response_model=UserProfile)
def update_me(data: UserUpdate, user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.put("/me/location")
def set_location(data: LocationUpdate, user: User = Depends(get_current_user)):
    """Точка проживания заяляется пользователем и НЕ верифицируется (решение N-2)."""
    raise NotImplementedError


@router.get("/me/history")
def get_history(user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.get("/{user_id}/public", response_model=UserPublic)
def public_profile(user_id: int):
    """Публичный профиль: имя, аватар, рейтинг. Телефон и адрес не раскрываются."""
    raise NotImplementedError
