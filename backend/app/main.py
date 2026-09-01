from fastapi import FastAPI

from app.api.root import router as root_router
from app.api.health import router as health_router
from app.api.about import router as about_router
from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.farms import router as farms_router
from app.api.fields import router as fields_router

from app.core.exceptions import UserAlreadyExistsError
from app.core.exception_handlers import (
    user_already_exists_handler,
)

app = FastAPI(
    title="MyCropAI API",
    version="1.0.0",
    description="Backend API for MyCropAI"
)


app.include_router(root_router)
app.include_router(health_router)
app.include_router(about_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(farms_router)
app.include_router(fields_router)

app.add_exception_handler(
    UserAlreadyExistsError,
    user_already_exists_handler,
)