from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.policies.farm_policy import require_farm_access
from app.repositories.farm import get_farm_by_id
from app.schemas.farm_overview import FarmOverviewResponse
from app.services.farm_overview import get_farm_overview_service


router = APIRouter(
    prefix="/api/v1/farms",
    tags=["Farm Digital Twin"],
)


@router.get(
    "/{farm_id}/overview",
    response_model=FarmOverviewResponse,
)
def get_farm_overview(
    farm_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_farm_by_id(
        db=db,
        farm_id=farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    require_farm_access(
        current_user=current_user,
        farm=farm,
    )

    return get_farm_overview_service(
        db=db,
        farm_id=farm_id,
    )