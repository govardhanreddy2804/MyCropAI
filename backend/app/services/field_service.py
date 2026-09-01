from uuid import UUID

from sqlalchemy.orm import Session

from app.models.field import Field

from app.repositories.field import (
    create_field,
    delete_field,
    get_fields_by_farm,
    update_field,
)


def create_farm_field(
    db: Session,
    farm_id: UUID,
    name: str,
    area: float,
    soil_type: str | None,
    location: str | None,
) -> Field:

    field = Field(
        farm_id=farm_id,
        name=name,
        area=area,
        soil_type=soil_type,
        location=location,
    )

    create_field(
        db,
        field,
    )

    db.commit()
    db.refresh(field)

    return field


def get_farm_fields(
    db: Session,
    farm_id: UUID,
) -> list[Field]:

    return get_fields_by_farm(
        db,
        farm_id,
    )


def update_farm_field(
    db: Session,
    field: Field,
    values: dict,
) -> Field:

    update_field(
        db=db,
        field=field,
        values=values,
    )

    db.commit()
    db.refresh(field)

    return field


def delete_farm_field(
    db: Session,
    field: Field,
) -> None:

    delete_field(
        db=db,
        field=field,
    )

    db.commit()