"""Use-case сервис профиля и геолокации (UC-2, UC-7).

Точка проживания заяляется пользователем и НЕ верифицируется (решение N-2):
расстояния в витрине — эвристика.
"""
from app.core.exceptions import NotFoundError
from app.domain.ports.repositories import ReviewRepository, UserRepository, WalletRepository


class ProfileService:
    def __init__(self, *, uow, users: UserRepository, wallets: WalletRepository,
                 reviews: ReviewRepository):
        self.uow = uow
        self.users = users
        self.wallets = wallets
        self.reviews = reviews

    def get_profile(self, user_id: int):
        user = self.users.get(user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    def update_profile(self, user_id: int, **fields):
        user = self.get_profile(user_id)
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        self.uow.commit()
        return user

    def set_location(self, user_id: int, lat: float, lon: float, address_text: str | None):
        user = self.get_profile(user_id)
        user.latitude = lat
        user.longitude = lon
        if address_text is not None:
            user.address_text = address_text
        self.uow.commit()
        return user

    def public_profile(self, user_id: int) -> dict:
        """Публичная карточка: имя, аватар, рейтинг. Телефон и адрес НЕ раскрываются."""
        user = self.get_profile(user_id)
        rating, cnt = self.reviews.rating_summary(user_id)
        return {"id": user.id, "name": user.name, "avatar_url": user.avatar_url,
                "rating": rating, "reviews_count": cnt}

    def profile_with_wallet(self, user_id: int) -> dict:
        user = self.get_profile(user_id)
        wallet = self.wallets.get_by_user(user_id)
        rating, cnt = self.reviews.rating_summary(user_id)
        return {
            "id": user.id, "phone": user.phone, "name": user.name, "bio": user.bio,
            "latitude": user.latitude, "longitude": user.longitude,
            "address_text": user.address_text,
            "role": getattr(user.role, "value", user.role),
            "status": getattr(user.status, "value", user.status),
            "rating": rating, "reviews_count": cnt,
            "wallet_total": wallet.total_balance if wallet else 0,
            "wallet_held": wallet.held_balance if wallet else 0,
        }
