from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.authorization import require_role
from app.dependencies.database import get_db

from app.models.enums import UserRole
from app.models.user import User

from app.policies.farm_policy import require_farm_access

from app.repositories.farm import get_farm_by_id

from app.schemas.farm import FarmCreate, FarmResponse

from app.services.farm_service import (
    create_user_farm,
    get_user_farms,
)

router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
)

@router.post(
    "",
    response_model=FarmResponse,
)
def create_farm_endpoint(
    request: FarmCreate,
    current_user: User = Depends(
        require_role(UserRole.FARMER)
    ),
    db: Session = Depends(get_db),
):
    return create_user_farm(
        db=db,
        user_id=current_user.id,
        name=request.name,
        location=request.location,
        area=request.area,
        soil_type=request.soil_type,
    )

@router.get(
    "",
    response_model=list[FarmResponse],
)
def list_farms(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    return get_user_farms(
        db,
        current_user.id,
    )

@router.get(
    "/{farm_id}",
    response_model=FarmResponse,
)
def get_farm(
    farm_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    return farm