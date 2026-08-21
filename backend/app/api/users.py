from fastapi import APIRouter, Depends

from app.schemas.user import UserCreate, UserResponse

from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.repositories.user import get_user_by_email

from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):

    created_user = {
        "id": 1,
        "name": user.name,
        "email": user.email,
        "password": user.password
    }

    return created_user


@router.get("/lookup")
def lookup_user(
    email: str,
    db: Session = Depends(get_db),
):
    user = get_user_by_email(
        db,
        email,
    )

    if user is None:
        return {
            "found": False
        }

    return {
        "found": True,
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
    }

@router.get("/me")
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }