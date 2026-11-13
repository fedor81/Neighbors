"""Composition root: единственное место, где порты связываются с адаптерами.

FastAPI-зависимости (app/api/deps.py) берут сервисы отсюда. Подмена реализаций
(Redis -> InMemory, S3 -> Local) — только здесь или через dependency_overrides в тестах.
"""
from functools import lru_cache

from app.core.config import settings
from app.domain.ports.repositories import CodeStoragePort, EventBusPort, SmsSenderPort
from app.infrastructure.eventbus_redis import InMemoryEventBus
from app.infrastructure.sms import ConsoleSmsSender, InMemoryCodeStorage


@lru_cache
def get_sms_sender() -> SmsSenderPort:
    # TODO(prod): по settings.SMS_PROVIDER выбирать реальный шлюз
    return ConsoleSmsSender()


@lru_cache
def get_code_storage() -> CodeStoragePort:
    # TODO(prod): RedisCodeStorage(settings.REDIS_URL)
    return InMemoryCodeStorage()


@lru_cache
def get_event_bus() -> EventBusPort:
    # TODO(prod): RedisEventBus(settings.REDIS_URL)
    return InMemoryEventBus()


@lru_cache
def get_file_storage():
    from app.infrastructure.storage_s3 import S3FileStorage  # лениво: boto3 не обязателен в тестах
    return S3FileStorage()
