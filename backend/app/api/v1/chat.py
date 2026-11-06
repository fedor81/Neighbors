"""Chat endpoints + WebSocket (UC-4). Чат привязан к бронированию — защита от спама."""
from fastapi import APIRouter, Depends, WebSocket

from app.api.deps import get_current_user
from app.models import User
from app.schemas import MessageCreate, MessageOut

router = APIRouter(tags=["chat"])


@router.get("/bookings/{booking_id}/messages", response_model=list[MessageOut])
def list_messages(booking_id: int, cursor: str | None = None, limit: int = 50,
                  user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.post("/bookings/{booking_id}/messages", response_model=MessageOut, status_code=201)
def send_message(booking_id: int, data: MessageCreate, user: User = Depends(get_current_user)):
    """Номера телефонов не раскрываются — вся коммуникация только здесь."""
    raise NotImplementedError


@router.post("/bookings/{booking_id}/messages/read")
def mark_read(booking_id: int, until_message_id: int, user: User = Depends(get_current_user)):
    raise NotImplementedError


@router.get("/chats/unread-count")
def unread_count(user: User = Depends(get_current_user)):
    raise NotImplementedError


# WebSocket: wss://.../api/v1/ws/bookings/{booking_id}/chat (JWT в query/message).
async def chat_websocket(websocket: WebSocket, booking_id: int):
    raise NotImplementedError  # TODO: accept + Redis Pub/Sub broadcast
