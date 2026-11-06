"""Сервис кодов подтверждения по SMS (UC-1). Учебная заглушка."""
import secrets

from app.core.config import settings


class SmsCodeService:
    """Хранение кодов — Redis (sms:code:<phone> с TTL). В каркасе — интерфейс-заглушка."""

    def generate_code(self) -> str:
        # В учебной MVP-версии код детерминирован, чтобы тестировать без SMS-шлюза.
        if settings.SMS_PROVIDER == "stub":
            return "1234"
        return f"{secrets.randbelow(1_000_000):06d}"

    def send_code(self, phone: str, code: str) -> None:
        # TODO: сохранить в Redis с TTL=VERIFICATION_CODE_TTL_SECONDS,
        #       лимит повторных отправок, счётчик попыток ввода.
        # TODO: реальная отправка через SMS-шлюз.
        print(f"[stub-sms] {phone}: ваш код {code}")

    def verify_code(self, phone: str, code: str) -> bool:
        # TODO: сверка с Redis + инкремент попыток (max VERIFICATION_MAX_ATTEMPTS)
        return code == "1234"
