"""Bookings endpoints (UC-3, UC-4, UC-5).

Жизненный цикл: pending -> approved/rejected -> rented -> returned/disputed/cancelled
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.schemas import BookingCreate, BookingOut
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(data: BookingCreate, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Создать заявку. Атомарно холдирует залог (если > 0); при нехватке средств — 400."""
    return BookingService(db).create_booking(user, data.item_id, data.start_date, data.end_date)


@router.get("/me", response_model=list[BookingOut])
def my_bookings(as_role: str = "renter", status: str | None = None,
                user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError


# --- действия владельца ---
@router.post("/{booking_id}/approve", response_model=BookingOut)
def approve(booking_id: int, user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    return BookingService(db).approve(booking_id, user.id)


@router.post("/{booking_id}/reject", response_model=BookingOut)
def reject(booking_id: int, user: User = Depends(get_current_user),
           db: Session = Depends(get_db)):
    return BookingService(db).reject(booking_id, user.id)


@router.post("/{booking_id}/confirm-return", response_model=BookingOut)
def confirm_return(booking_id: int, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    """Вещь получена без повреждений -> разморозка залога, статус returned."""
    return BookingService(db).confirm_return(booking_id, user.id)


@router.post("/{booking_id}/report-issue", response_model=BookingOut)
def report_issue(booking_id: int, reason: str, user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """Порча вещи -> спорная ситуация, разморозка заблокирована, подключается модератор."""
    return BookingService(db).report_issue(booking_id, user.id, reason)


# --- действия арендатора ---
@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel(booking_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError  # отмена до ответа владельца: залог -> release, вещь -> available


@router.post("/{booking_id}/confirm-receipt", response_model=BookingOut)
def confirm_receipt(booking_id: int, user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    """«Вещь у меня, всё отлично» -> старт таймера аренды."""
    return BookingService(db).confirm_receipt(booking_id, user.id)


@router.post("/{booking_id}/refuse-on-inspection", response_model=BookingOut)
def refuse_on_inspection(booking_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError  # отказ при осмотре: залог release, сделка аннулируется


@router.post("/{booking_id}/initiate-return", response_model=BookingOut)
def initiate_return(booking_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError  # уведомление владельцу о готовности вернуть


# --- оценки (UC-5) ---
@router.post("/{booking_id}/reviews")
def leave_review(booking_id: int, user: User = Depends(get_current_user)):
    """Оценка 1-5 + отзыв. Не публикуется второй стороне до встречной оценки или истечения срока."""
    raise NotImplementedError


@router.get("/{booking_id}/reviews")
def booking_reviews(booking_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError
