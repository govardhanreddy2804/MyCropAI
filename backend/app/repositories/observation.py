from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.observation import AgriculturalObservation


def create_observation(
    db: Session,
    observation: AgriculturalObservation,
) -> AgriculturalObservation:

    db.add(observation)
    db.flush()

    return observation


def get_observation_by_id(
    db: Session,
    observation_id: UUID,
) -> AgriculturalObservation | None:

    statement = select(AgriculturalObservation).where(
        AgriculturalObservation.id == observation_id
    )

    return db.scalar(statement)


def get_observations_by_field(
    db: Session,
    field_id: UUID,
) -> list[AgriculturalObservation]:

    statement = (
        select(AgriculturalObservation)
        .where(
            AgriculturalObservation.field_id == field_id
        )
        .order_by(
            AgriculturalObservation.observed_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def delete_observation(
    db: Session,
    observation: AgriculturalObservation,
) -> None:

    db.delete(observation)
    db.flush()