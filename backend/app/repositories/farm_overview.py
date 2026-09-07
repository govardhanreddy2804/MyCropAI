from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.farm import Farm
from app.models.field import Field

def get_farm_overview(
    db: Session,
    farm_id: UUID,
) -> Farm | None:

    statement = (
        select(Farm)
        .where(Farm.id == farm_id)
        .options(
            selectinload(Farm.fields)
            .selectinload(Field.crops)
        )
    )

    return db.scalar(statement)