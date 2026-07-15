from fastapi import APIRouter
from fastapi import Depends
from app.dependencies.common import get_app_name

router = APIRouter()


@router.get("/")
def root(app_name: str = Depends(get_app_name)):
    return {
        "message": f"Welcome to {app_name}"
    }