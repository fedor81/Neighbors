"""EventBusPort -> Redis Pub/Sub (real-time чат и уведомления, открытый вопрос №1)."""
import json
from typing import Any

from app.domain.ports.repositories import EventBusPort


class InMemoryEventBus(EventBusPort):
    """Заглушка для одного процесса/тестов."""

    def __init__(self):
        self.events: list[tuple[str, dict[str, Any]]] = []

    def publish(self, channel: str, payload: dict[str, Any]) -> None:
        self.events.append((channel, payload))


class RedisEventBus(EventBusPort):
    """TODO(prod): redis client .publish(channel, json.dumps(payload));
    WS-подписчики читают через pubsub.listen() в отдельной задаче asyncio."""

    def publish(self, channel: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    @staticmethod
    def encode(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, default=str)
