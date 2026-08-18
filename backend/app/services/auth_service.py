from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import (
    create_user,
    get_user_by_email,
)

def register_user(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> User:

    existing_user = get_user_by_email(
        db,
        email,
    )

    if existing_user:
        raise ValueError(
            "A user with this email already exists"
        )

    password_hash = hash_password(password)

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    return create_user(db, user)