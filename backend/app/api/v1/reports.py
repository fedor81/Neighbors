"""Reports endpoints (UC-10). Автор жалобы скрыт от целевого пользователя."""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas import ReportCreate

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=202)
def create_report(data: ReportCreate, user: User = Depends(get_current_user)):
    raise NotImplementedError  # создать Dispute(item|message|user), пометить цель


@router.get("/me")
def my_reports(user: User = Depends(get_current_user)):
    raise NotImplementedError
