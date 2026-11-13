"""Адаптеры портов SMS и хранилища кодов (UC-1).

В production: SmsSenderPort -> интеграция с SMS-шлюзом, CodeStoragePort -> Redis.
Для учебного MVP оба реализованы in-memory заглушками.
"""
import secrets
import time

from app.domain.ports.repositories import CodeStoragePort, SmsSenderPort


class ConsoleSmsSender(SmsSenderPort):
    """Пишет SMS в stdout — замена SMS-шлюза для локальной разработки."""

    def send(self, phone: str, text: str) -> None:
        print(f"[stub-sms] -> {phone}: {text}")


class InMemoryCodeStorage(CodeStoragePort):
    """Хранение кодов в памяти процесса. НЕ для прода (нужен Redis с TTL)."""

    def __init__(self):
        # phone -> (code, expires_at, attempts)
        self._codes: dict[str, tuple[str, float, int]] = {}
        self._last_sent: dict[str, float] = {}

    def save(self, phone: str, code: str, ttl_seconds: int) -> None:
        self._codes[phone] = (code, time.monotonic() + ttl_seconds, 0)
        self._last_sent[phone] = time.monotonic()

    def check_and_consume(self, phone: str, code: str, max_attempts: int) -> bool:
        entry = self._codes.get(phone)
        if not entry:
            return False
        stored, expires_at, attempts = entry
        if time.monotonic() > expires_at:
            del self._codes[phone]
            return False
        if attempts >= max_attempts:
            del self._codes[phone]
            return False
        if stored == code:
            del self._codes[phone]  # одноразовый код
            return True
        self._codes[phone] = (stored, expires_at, attempts + 1)
        return False

    def can_resend(self, phone: str, cooldown_seconds: int) -> bool:
        last = self._last_sent.get(phone)
        return last is None or (time.monotonic() - last) >= cooldown_seconds


class RedisCodeStorage(CodeStoragePort):
    """TODO(prod): ключи sms:code:<phone> (SET EX ttl), sms:attempts:<phone> (INCR+EXPIRE),
    sms:cooldown:<phone> (SET NX EX). Использует redis.Redis из app.core.config.REDIS_URL."""

    def save(self, phone: str, code: str, ttl_seconds: int) -> None:
        raise NotImplementedError

    def check_and_consume(self, phone: str, code: str, max_attempts: int) -> bool:
        raise NotImplementedError

    def can_resend(self, phone: str, cooldown_seconds: int) -> bool:
        raise NotImplementedError


def generate_code(stub_mode: bool) -> str:
    """В учебном MVP код детерминирован ('1234') — можно тестировать без шлюза."""
    if stub_mode:
        return "1234"
    return f"{secrets.randbelow(1_000_000):06d}"
