from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crop import Crop


def create_crop(
    db: Session,
    crop: Crop,
) -> Crop:

    db.add(crop)
    db.flush()

    return crop


def get_crop_by_id(
    db: Session,
    crop_id: UUID,
) -> Crop | None:

    statement = select(Crop).where(
        Crop.id == crop_id
    )

    return db.scalar(statement)


def get_crops_by_field(
    db: Session,
    field_id: UUID,
) -> list[Crop]:

    statement = (
        select(Crop)
        .where(Crop.field_id == field_id)
        .order_by(Crop.planting_date)
    )

    return list(
        db.scalars(statement).all()
    )


def update_crop(
    db: Session,
    crop: Crop,
    values: dict,
) -> Crop:

    for field, value in values.items():
        setattr(crop, field, value)

    db.flush()

    return crop


def delete_crop(
    db: Session,
    crop: Crop,
) -> None:

    db.delete(crop)
    db.flush()