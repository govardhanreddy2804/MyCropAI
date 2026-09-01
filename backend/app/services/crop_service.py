from uuid import UUID

from sqlalchemy.orm import Session

from app.models.crop import Crop, CropStatus

from app.repositories.crop import (
    create_crop,
    delete_crop,
    get_crops_by_field,
    update_crop,
)


def create_field_crop(
    db: Session,
    field_id: UUID,
    crop_type: str,
    variety: str | None,
    planting_date,
    expected_harvest_date,
) -> Crop:

    crop = Crop(
        field_id=field_id,
        crop_type=crop_type,
        variety=variety,
        planting_date=planting_date,
        expected_harvest_date=expected_harvest_date,
        status=CropStatus.PLANNED,
    )

    create_crop(
        db,
        crop,
    )

    db.commit()
    db.refresh(crop)

    return crop


def get_field_crops(
    db: Session,
    field_id: UUID,
) -> list[Crop]:

    return get_crops_by_field(
        db,
        field_id,
    )


def update_field_crop(
    db: Session,
    crop: Crop,
    values: dict,
) -> Crop:

    update_crop(
        db=db,
        crop=crop,
        values=values,
    )

    db.commit()
    db.refresh(crop)

    return crop


def delete_field_crop(
    db: Session,
    crop: Crop,
) -> None:

    delete_crop(
        db=db,
        crop=crop,
    )

    db.commit()