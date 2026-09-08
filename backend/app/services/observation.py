from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import ObservationSource
from app.models.observation import AgriculturalObservation
from app.repositories.observation import (
    create_observation,
    delete_observation,
    get_observation_by_id,
    get_observations_by_field,
)

from app.services.observation_resolver import (
    resolve_best_observations,
)

def create_field_observation(
    db: Session,
    field_id: UUID,
    observation_type,
    value: float,
    unit: str,
    source: ObservationSource,
    observed_at: datetime,
    confidence: float | None,
) -> AgriculturalObservation:

    observation = AgriculturalObservation(
        field_id=field_id,
        observation_type=observation_type,
        value=value,
        unit=unit,
        source=source,
        observed_at=observed_at,
        confidence=confidence,
    )

    create_observation(
        db=db,
        observation=observation,
    )

    db.commit()
    db.refresh(observation)

    return observation


def get_field_observations(
    db: Session,
    field_id: UUID,
) -> list[AgriculturalObservation]:

    return get_observations_by_field(
        db=db,
        field_id=field_id,
    )


def delete_field_observation(
    db: Session,
    observation_id: UUID,
) -> None:

    observation = get_observation_by_id(
        db=db,
        observation_id=observation_id,
    )

    if observation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Observation not found",
        )

    delete_observation(
        db=db,
        observation=observation,
    )

    db.commit()

def get_best_field_observations(
    db: Session,
    field_id: UUID,
):
    observations = get_observations_by_field(
        db=db,
        field_id=field_id,
    )

    return resolve_best_observations(
        observations
    )