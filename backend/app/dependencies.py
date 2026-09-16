from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    try:
        user_id = UUID(payload["sub"])
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token subject") from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(*roles: str):
    allowed = {role.upper() for role in roles}

    def dependency(user: User = Depends(current_user)) -> User:
        if user.role.name.upper() not in allowed:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return dependency
