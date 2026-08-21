from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.core.tokens import (
    generate_refresh_token,
    hash_refresh_token,
)
from app.core.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    RefreshTokenReuseError,
)

from app.models.refresh_session import RefreshSession
from app.models.user import User

from app.repositories.refresh_session import (
    create_refresh_session,
    get_refresh_session_by_token_hash,
)
from app.repositories.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
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

def create_refresh_session_for_user(
    db: Session,
    user: User,
) -> str:

    raw_token = generate_refresh_token()

    token_hash = hash_refresh_token(
        raw_token
    )

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(
            days=settings.refresh_token_expire_days
        )
    )

    session = RefreshSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    create_refresh_session(
        db,
        session,
    )

    return raw_token


def refresh_access_token(
    db: Session,
    refresh_token: str,
):

    token_hash = hash_refresh_token(
        refresh_token
    )

    session = get_refresh_session_by_token_hash(
        db,
        token_hash,
    )

    if session is None:
        raise InvalidRefreshTokenError(
            "Invalid refresh token"
        )

    if session.revoked_at is not None:
        raise RefreshTokenReuseError(
            "Refresh token has already been used"
        )

    if session.expires_at <= datetime.now(
        timezone.utc
    ):
        raise InvalidRefreshTokenError(
            "Refresh token has expired"
        )

    user = get_user_by_id(
        db,
        session.user_id,
    )

    if user is None or not user.is_active:
        raise InvalidRefreshTokenError(
            "Invalid refresh token"
        )

    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role,
    )

    new_raw_token = generate_refresh_token()

    new_token_hash = hash_refresh_token(
        new_raw_token
    )

    new_session = RefreshSession(
        user_id=user.id,
        token_hash=new_token_hash,
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                days=settings.refresh_token_expire_days
            )
        ),
    )

    try:
        create_refresh_session(
            db,
            new_session,
        )

        session.revoked_at = datetime.now(
            timezone.utc
        )

        session.replaced_by_id = new_session.id

        db.commit()

    except Exception:
        db.rollback()
        raise

    return access_token, new_raw_token