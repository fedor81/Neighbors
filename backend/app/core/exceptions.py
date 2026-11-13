"""Доменные исключения (application-independent).

Поднимаются сервисным слоем, мапятся в HTTP в presentation-слое
(app/api/error_handlers.py). Presentation не должен знать про FastAPI-HTTPException
внутри бизнес-логики.
"""


class DomainError(Exception):
    """База доменных ошибок. code — стабильный машинный код для клиента."""
    code: str = "DOMAIN_ERROR"
    http_status: int = 400

    def __init__(self, message: str = ""):
        self.message = message or self.__doc__ or self.code
        super().__init__(self.message)


class NotFoundError(DomainError):
    """Запрошенная сущность не существует или недоступна текущему пользователю."""
    code = "NOT_FOUND"
    http_status = 404


class PermissionDeniedError(DomainError):
    """Действие запрещено: не владелец, заблокирован, не та роль."""
    code = "PERMISSION_DENIED"
    http_status = 403


class ConflictError(DomainError):
    """Нарушение инварианта состояния (вещь уже занята и т.п.)."""
    code = "CONFLICT"
    http_status = 409


class InsufficientFundsError(DomainError):
    """Недостаточно средств на балансе для холдирования залога (UC-3)."""
    code = "INSUFFICIENT_FUNDS"
    http_status = 400


class InvalidStateTransitionError(DomainError):
    """Переход брони вне разрешённой машины состояний."""
    code = "INVALID_STATE_TRANSITION"
    http_status = 400


class ProhibitedItemError(DomainError):
    """Услуги, еда, медикаменты запрещены к размещению (UC-6)."""
    code = "PROHIBITED_ITEM"
    http_status = 422
