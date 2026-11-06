"""Pydantic-схемы запросов/ответов API (каркас)."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Auth (UC-1) ----------
class SendCodeRequest(BaseModel):
    phone: str = Field(pattern=r"^\+?[78][-\( ]?\d{3}[-\) ]?\d{3}[-\s]?\d{2}[-\s]?\d{2}$")


class VerifyCodeRequest(BaseModel):
    phone: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    is_new_user: bool
    user: "UserPublic"


class RefreshRequest(BaseModel):
    refresh_token: str


# ---------- Users / Profile (UC-2, UC-7) ----------
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None = None
    avatar_url: str | None = None
    rating: float | None = None
    reviews_count: int = 0


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone: str
    name: str | None = None
    bio: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    address_text: str | None = None
    role: str
    status: str
    wallet_total: Decimal = Decimal("0")
    wallet_held: Decimal = Decimal("0")


class UserUpdate(BaseModel):
    name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None


class LocationUpdate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    address_text: str | None = None


# ---------- Categories ----------
class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    icon_url: str | None = None


# ---------- Items (UC-6) ----------
class ItemCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str | None = None
    category_id: int
    deposit_amount: Decimal = Decimal("0")
    format: str = "free"  # free | barter | money


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    category: CategoryOut
    deposit_amount: Decimal
    status: str
    owner: UserPublic
    main_photo_url: str | None = None
    distance_m: int | None = None  # только в выдаче; адрес владельца не раскрывается


# ---------- Bookings (UC-3..5) ----------
class BookingCreate(BaseModel):
    item_id: int
    start_date: datetime
    end_date: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    renter_id: int
    status: str
    deposit_held_amount: Decimal
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime


# ---------- Chat (UC-4) ----------
class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime


# ---------- Reviews (UC-5) ----------
class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: str | None
    is_visible: bool
    created_at: datetime


# ---------- Wallet (UC-7) ----------
class WalletOut(BaseModel):
    total: Decimal
    held: Decimal
    available: Decimal


class TopUpRequest(BaseModel):
    amount: Decimal = Field(gt=0)


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    amount: Decimal
    booking_id: int | None
    created_at: datetime


# ---------- Notifications (UC-8) ----------
class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    message: str
    is_read: bool
    created_at: datetime


# ---------- Reports / Disputes (UC-9, UC-10) ----------
class ReportCreate(BaseModel):
    target_type: str = Field(pattern="^(item|message|user)$")
    target_id: int
    reason: str = Field(min_length=10)


class DisputeResolve(BaseModel):
    action: str = Field(pattern="^(refund|charge|dismiss)$")
    comment: str
    ban_user: bool = False


# ---------- Errors ----------
class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


TokenResponse.model_rebuild()
ItemOut.model_rebuild()
