from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
)
from app.services.auth_service import register_user


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