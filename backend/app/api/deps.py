"""FastAPI-зависимости: БД, текущий пользователь, роли."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models import User, UserStatus

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")

    user = db.get(User, int(payload["sub"]))
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status == UserStatus.blocked:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is blocked")
    return user


def require_moderator(user: User = Depends(get_current_user)) -> User:
    if user.role != "moderator":
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Moderator role required")
    return user
