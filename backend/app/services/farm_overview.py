from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.farm_overview import get_farm_overview


def get_farm_overview_service(
    db: Session,
    farm_id: UUID,
):
    farm = get_farm_overview(
        db=db,
        farm_id=farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    field_count = len(farm.fields)

    crop_count = sum(
        len(field.crops)
        for field in farm.fields
    )

    return {
        "id": farm.id,
        "name": farm.name,
        "location": farm.location,
        "area": farm.area,
        "soil_type": farm.soil_type,
        "field_count": field_count,
        "crop_count": crop_count,
        "fields": farm.fields,
    }