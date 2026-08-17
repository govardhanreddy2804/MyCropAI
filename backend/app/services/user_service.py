from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user import (
    create_user,
    get_user_by_email,
)

def register_user(
    db: Session,
    name: str,
    email: str,
    password_hash: str,
) -> User:

    existing_user = get_user_by_email(
        db,
        email,
    )

    if existing_user:
        raise ValueError(
            "A user with this email already exists"
        )

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    return create_user(db, user)