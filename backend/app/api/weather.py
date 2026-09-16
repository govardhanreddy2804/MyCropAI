from uuid import UUID

from app.services.weather.factory import get_weather_provider
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.policies.farm_policy import require_farm_access
from app.repositories.farm import get_farm_by_id
from app.repositories.field import get_field_by_id
from app.services.weather.openweather import OpenWeatherProvider
from app.services.weather.service import ingest_current_weather


router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/fields/{field_id}/weather",
    tags=["Weather"],
)


def _get_authorized_field(
    db: Session,
    farm_id: UUID,
    field_id: UUID,
    current_user: User,
):
    farm = get_farm_by_id(db, farm_id)

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    require_farm_access(current_user, farm)

    field = get_field_by_id(db, field_id)

    if field is None or field.farm_id != farm.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found",
        )

    return field


@router.post("/current")
def fetch_current_weather(
    farm_id: UUID,
    field_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    field = _get_authorized_field(
        db=db,
        farm_id=farm_id,
        field_id=field_id,
        current_user=current_user,
    )

    if field.latitude is None or field.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field coordinates are required for weather data",
        )

    provider = get_weather_provider()

    try:
        observations = ingest_current_weather(
            db=db,
            field_id=field.id,
            provider=provider,
            latitude=field.latitude,
            longitude=field.longitude,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    db.commit()

    return observations