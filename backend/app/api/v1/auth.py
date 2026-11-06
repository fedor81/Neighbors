"""Auth endpoints (UC-1): верификация только по номеру телефона."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import SendCodeRequest, VerifyCodeRequest, TokenResponse, UserPublic
from app.services.auth_service import SmsCodeService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/phone/send-code", status_code=202)
def send_code(data: SendCodeRequest):
    """Запрос SMS-кода. Повторная отправка ограничена таймаутом (TODO: rate-limit в Redis)."""
    svc = SmsCodeService()
    code = svc.generate_code()
    svc.send_code(data.phone, code)
    return {"detail": "code_sent"}


@router.post("/phone/verify", response_model=TokenResponse)
def verify_code(data: VerifyCodeRequest, db: Session = Depends(get_db)):
    """Подтверждение кода -> JWT. При повторном входе авторизует существующий аккаунт."""
    # TODO: SmsCodeService.verify_code + поиск/создание User + Wallet, генерация токенов
    raise NotImplementedError("каркас: реализовать UC-1")
