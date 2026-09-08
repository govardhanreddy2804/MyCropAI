from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.policies.farm_policy import require_farm_access
from app.repositories.farm import get_farm_by_id
from app.repositories.field import get_field_by_id
from app.repositories.observation import get_observation_by_id
from app.schemas.observation import (
    ObservationCreate,
    ObservationResponse,
)
from app.services.observation import (
    create_field_observation,
    delete_field_observation,
    get_field_observations,
)


router = APIRouter(
    prefix="/api/v1/farms",
    tags=["Agricultural Observations"],
)


@router.post(
    "/{farm_id}/fields/{field_id}/observations",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_observation(
    farm_id: UUID,
    field_id: UUID,
    payload: ObservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_farm_by_id(
        db=db,
        farm_id=farm_id,
    )

    if farm is None:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user=current_user,
        farm=farm,
    )

    field = get_field_by_id(
        db=db,
        field_id=field_id,
    )

    if field is None or field.farm_id != farm.id:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    return create_field_observation(
        db=db,
        field_id=field_id,
        observation_type=payload.observation_type,
        value=payload.value,
        unit=payload.unit,
        source=payload.source,
        observed_at=payload.observed_at,
        confidence=payload.confidence,
    )


@router.get(
    "/{farm_id}/fields/{field_id}/observations",
    response_model=list[ObservationResponse],
)
def list_observations(
    farm_id: UUID,
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_farm_by_id(
        db=db,
        farm_id=farm_id,
    )

    if farm is None:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user=current_user,
        farm=farm,
    )

    field = get_field_by_id(
        db=db,
        field_id=field_id,
    )

    if field is None or field.farm_id != farm.id:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    return get_field_observations(
        db=db,
        field_id=field_id,
    )


@router.delete(
    "/{farm_id}/fields/{field_id}/observations/{observation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_observation(
    farm_id: UUID,
    field_id: UUID,
    observation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    farm = get_farm_by_id(
        db=db,
        farm_id=farm_id,
    )

    if farm is None:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user=current_user,
        farm=farm,
    )

    field = get_field_by_id(
        db=db,
        field_id=field_id,
    )

    if field is None or field.farm_id != farm.id:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    observation = get_observation_by_id(
        db=db,
        observation_id=observation_id,
    )

    if observation is None or observation.field_id != field.id:
        # from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Observation not found",
        )

    delete_field_observation(
        db=db,
        observation_id=observation_id,
    )