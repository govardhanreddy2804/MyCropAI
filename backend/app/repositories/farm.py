from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.farm import Farm

def create_farm(
    db: Session,
    farm: Farm,
) -> Farm:

    db.add(farm)
    db.flush()

    return farm

def get_farm_by_id(
    db: Session,
    farm_id: UUID,
) -> Farm | None:

    statement = select(Farm).where(
        Farm.id == farm_id
    )

    return db.scalar(statement)

def get_farms_by_owner(
    db: Session,
    owner_id: UUID,
) -> list[Farm]:

    statement = select(Farm).where(
        Farm.owner_id == owner_id
    )

    return list(
        db.scalars(statement).all()
    )