from sqlalchemy.orm import Session

from app.models import User
from app.repositories import get_role, get_user_by_email
from app.security import hash_password, verify_password


def register_user(db: Session, email: str, password: str, role_name: str = "customer") -> User:
    if get_user_by_email(db, email):
        raise ValueError("User already exists")
    role = get_role(db, role_name)
    if role is None:
        raise ValueError("Invalid role")
    user = User(email=email.lower(), password_hash=hash_password(password), role_id=role.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user
