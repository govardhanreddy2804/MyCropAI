from uuid import UUID

from sqlalchemy.orm import Session

from app.models.field import Field
from app.services.weather.service import ingest_current_weather


def sync_field_weather(
    db: Session,
    field_id: UUID,
) -> None:
    """Synchronize current weather observations for a field."""

    field = db.get(Field, field_id)

    if field is None:
        return

    if field.latitude is None or field.longitude is None:
        return

    ingest_current_weather(
        db=db,
        field=field,
    )
