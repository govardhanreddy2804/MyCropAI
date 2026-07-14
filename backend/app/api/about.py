from fastapi import APIRouter

router = APIRouter()


@router.get("/about")
def about():
    return {
        "project": "MyCropAI",
        "backend": "FastAPI",
        "version": "1.0.0"
    }