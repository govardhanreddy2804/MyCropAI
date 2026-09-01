from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.field import Field


def create_field(
    db: Session,
    field: Field,
) -> Field:

    db.add(field)
    db.flush()

    return field


def get_field_by_id(
    db: Session,
    field_id: UUID,
) -> Field | None:

    statement = select(Field).where(
        Field.id == field_id
    )

    return db.scalar(statement)


def get_fields_by_farm(
    db: Session,
    farm_id: UUID,
) -> list[Field]:

    statement = (
        select(Field)
        .where(Field.farm_id == farm_id)
        .order_by(Field.name)
    )

    return list(
        db.scalars(statement).all()
    )


def update_field(
    db: Session,
    field: Field,
    values: dict,
) -> Field:

    for key, value in values.items():
        setattr(field, key, value)

    db.flush()

    return field


def delete_field(
    db: Session,
    field: Field,
) -> None:

    db.delete(field)
    db.flush()