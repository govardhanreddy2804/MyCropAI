from uuid import UUID

from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.repositories.farm import (
    create_farm,
    get_farm_by_id,
    get_farms_by_owner,
)

def create_user_farm(
    db: Session,
    user_id: UUID,
    name: str,
    location: str,
    area: float,
    soil_type: str | None,
) -> Farm:

    farm = Farm(
        owner_id=user_id,
        name=name,
        location=location,
        area=area,
        soil_type=soil_type,
    )

    create_farm(db, farm)

    db.commit()
    db.refresh(farm)

    return farm

def get_user_farms(
    db: Session,
    user_id: UUID,
) -> list[Farm]:

    return get_farms_by_owner(
        db,
        user_id,
    )