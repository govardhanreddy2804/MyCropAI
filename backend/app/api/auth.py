from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InvalidRefreshTokenError
from app.core.jwt import create_access_token
from app.core.tokens import hash_refresh_token

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

from app.models.user import User

from app.repositories.refresh_session import (
    get_refresh_session_by_token_hash,
    get_active_refresh_sessions_for_user,
)

from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

from app.services.auth_service import (
    authenticate_user,
    create_refresh_session_for_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password,
        )

        return user

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):

    user = authenticate_user(
        db=db,
        email=request.email,
        password=request.password,
    )

    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role,
    )

    refresh_token = create_refresh_session_for_user(
        db=db,
        user=user,
    )

    db.commit()

    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=(settings.refresh_token_expire_days * 24 * 60 * 60),path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias=settings.refresh_cookie_name,
    ),
    db: Session = Depends(get_db),
):
    if refresh_token is None:
        raise InvalidRefreshTokenError(
            "Refresh token is missing"
        )

    access_token, new_refresh_token = (
        refresh_access_token(
            db,
            refresh_token,
        )
    )

    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=new_refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.refresh_token_expire_days * 86400,
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias=settings.refresh_cookie_name,
    ),
    db: Session = Depends(get_db),
):
    if refresh_token:
        token_hash = hash_refresh_token(
            refresh_token
        )

        session = get_refresh_session_by_token_hash(
            db,
            token_hash,
        )

        if session and session.revoked_at is None:
            session.revoked_at = datetime.now(
                timezone.utc
            )
            db.commit()

    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path="/api/v1/auth",
    )

    return {
        "message": "Logged out successfully"
    }

@router.post("/logout-all")
def logout_all(
    response: Response,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    sessions = get_active_refresh_sessions_for_user(
    db,
    current_user.id,
)

    

    response.delete_cookie(
    key=settings.refresh_cookie_name,
    path="/api/v1/auth",
)

    return {
    "message": "All sessions have been logged out"
}