from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import (register_user, authenticate_user, create_refresh_session_for_user)

from app.core.jwt import create_access_token
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
)

from app.core.config import settings

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
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )