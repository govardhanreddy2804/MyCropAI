from fastapi import FastAPI

from app.api.root import router as root_router
from app.api.health import router as health_router
from app.api.about import router as about_router

app = FastAPI(
    title="MyCropAI API",
    version="1.0.0",
    description="Backend API for MyCropAI"
)


app.include_router(root_router)
app.include_router(health_router)
app.include_router(about_router)