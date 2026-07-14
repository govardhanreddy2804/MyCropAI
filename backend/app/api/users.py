from fastapi import APIRouter

from app.schemas.user import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/")
def create_user(user: UserCreate):

    return {
        "message": "User received",
        "data": user
    }