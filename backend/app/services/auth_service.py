from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import (
    create_user,
    get_user_by_email,
)

from sqlalchemy.exc import IntegrityError
from app.core.exceptions import UserAlreadyExistsError

from app.core.exceptions import (
    InvalidCredentialsError,
)
from app.core.security import verify_password
from app.repositories.user import get_user_by_email

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
        raise UserAlreadyExistsError(
            "A user with this email already exists"
        )

    password_hash = hash_password(password)

    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    try:
        create_user(db, user)

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()

        raise UserAlreadyExistsError(
            "A user with this email already exists"
        ) from None

def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:

    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    if not user.is_active:
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise InvalidCredentialsError(
            "Invalid email or password"
        )

    return user