from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import (
    CropStatus,
    ObservationSource,
    ObservationType,
    UserRole,
)
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.observation import AgriculturalObservation
from app.models.field import Field
from app.models.user import User
from app.services.irrigation.recommendation import (
    generate_irrigation_recommendation,
)


def test_generate_irrigation_recommendation(db_session):
    user = User(
        id=uuid4(),
        name="Irrigation Test User",
        email=f"irrigation-{uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.FARMER,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    farm = Farm(
        id=uuid4(),
        owner_id=user.id,
        name="Irrigation Test Farm",
        location="Hyderabad",
        area=5.0,
    )

    db_session.add(farm)
    db_session.flush()

    field = Field(
        id=uuid4(),
        farm_id=farm.id,
        name="Field 1",
        area=1.0,
        soil_type="loamy",
    )

    db_session.add(field)
    db_session.flush()

    crop = Crop(
        id=uuid4(),
        field_id=field.id,
        crop_type="maize",
        planting_date=datetime.now(
            timezone.utc
        ).date(),
        status=CropStatus.ACTIVE,
    )

    db_session.add(crop)
    db_session.flush()

    observed_at = datetime.now(timezone.utc)

    observations = [
        AgriculturalObservation(
            field_id=field.id,
            observation_type=ObservationType.SOIL_MOISTURE,
            value=20,
            unit="percent",
            source=ObservationSource.MANUAL,
            observed_at=observed_at,
            confidence=0.9,
        ),
        AgriculturalObservation(
            field_id=field.id,
            observation_type=ObservationType.RAINFALL,
            value=0,
            unit="mm",
            source=ObservationSource.WEATHER_API,
            observed_at=observed_at,
            confidence=0.8,
        ),
        AgriculturalObservation(
            field_id=field.id,
            observation_type=ObservationType.AIR_TEMPERATURE,
            value=32,
            unit="celsius",
            source=ObservationSource.WEATHER_API,
            observed_at=observed_at,
            confidence=0.8,
        ),
        AgriculturalObservation(
            field_id=field.id,
            observation_type=ObservationType.AIR_HUMIDITY,
            value=45,
            unit="percent",
            source=ObservationSource.WEATHER_API,
            observed_at=observed_at,
            confidence=0.8,
        ),
    ]

    db_session.add_all(observations)
    db_session.flush()

    result = generate_irrigation_recommendation(
        db=db_session,
        field=field,
        crop=crop,
    )

    assert result["irrigation_required"] is True
    assert result["water_required_liters"] > 0
    assert result["recommended_duration_minutes"] is None
    assert result["soil_moisture"] == 20