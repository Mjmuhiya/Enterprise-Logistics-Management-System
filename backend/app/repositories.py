from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role, User


def get_role(db: Session, name: str) -> Role | None:
    return db.scalar(select(Role).where(Role.name == name))


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))
