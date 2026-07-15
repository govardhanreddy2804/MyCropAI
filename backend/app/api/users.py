from fastapi import APIRouter

from app.schemas.user import UserCreate, UserResponse

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