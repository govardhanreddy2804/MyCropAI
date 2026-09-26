from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.policies.farm_policy import require_farm_access
from app.repositories.crop import get_crop_by_id
from app.repositories.farm import get_farm_by_id
from app.repositories.field import get_field_by_id
from app.services.irrigation.recommendation import (
    generate_irrigation_recommendation,
)
from app.schemas.irrigation import (
    IrrigationRecommendationResponse,
)


router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/fields/{field_id}",
    tags=["Irrigation"],
)


def _get_authorized_field(
    db: Session,
    farm_id: UUID,
    field_id: UUID,
    current_user: User,
):
    farm = get_farm_by_id(db, farm_id)

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    require_farm_access(current_user, farm)

    field = get_field_by_id(db, field_id)

    if field is None or field.farm_id != farm.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found",
        )

    return field


@router.get(
    "/irrigation/recommendation",
    response_model=IrrigationRecommendationResponse,
)
def get_irrigation_recommendation(
    farm_id: UUID,
    field_id: UUID,
    crop_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    field = _get_authorized_field(
        db=db,
        farm_id=farm_id,
        field_id=field_id,
        current_user=current_user,
    )

    crop = get_crop_by_id(
        db=db,
        crop_id=crop_id,
    )

    if crop is None or crop.field_id != field.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    return generate_irrigation_recommendation(
        db=db,
        field=field,
        crop=crop,
    )