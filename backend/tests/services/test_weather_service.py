from datetime import datetime, timezone
from uuid import uuid4

from app.models.enums import (
    ObservationSource,
    ObservationType,
    UserRole,
)
from app.models.farm import Farm
from app.models.field import Field
from app.models.user import User
from app.services.weather.base import WeatherData
from app.services.weather.service import ingest_current_weather


class FakeWeatherProvider:
    def get_current_weather(self, latitude, longitude):
        return WeatherData(
            observed_at=datetime.now(timezone.utc),
            air_temperature=31.5,
            air_humidity=68.0,
            rainfall=2.5,
            wind_speed=4.2,
        )

    def get_forecast(
        self,
        latitude,
        longitude,
        start_at,
        end_at,
    ):
        return []


def test_ingest_current_weather(db_session):
    # ---------------------------------------------------------
    # Create a real user
    # ---------------------------------------------------------

    user = User(
        name="Weather Test User",
        email=f"weather-{uuid4()}@example.com",
        password_hash="test-password-hash",
        role=UserRole.FARMER,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    # ---------------------------------------------------------
    # Create a real farm
    # ---------------------------------------------------------

    farm = Farm(
        owner_id=user.id,
        name="Weather Test Farm",
        location="Hyderabad",
        area=5.0,
    )

    db_session.add(farm)
    db_session.flush()

    # ---------------------------------------------------------
    # Create a real field
    # ---------------------------------------------------------

    field = Field(
        farm_id=farm.id,
        name="Weather Test Field",
        area=2.0,
        latitude=17.385,
        longitude=78.4867,
    )

    db_session.add(field)
    db_session.flush()

    # ---------------------------------------------------------
    # Ingest weather
    # ---------------------------------------------------------

    observations = ingest_current_weather(
        db=db_session,
        field_id=field.id,
        provider=FakeWeatherProvider(),
        latitude=17.385,
        longitude=78.4867,
    )

    # ---------------------------------------------------------
    # Assertions
    # ---------------------------------------------------------

    assert len(observations) == 4

    types = {
        observation.observation_type
        for observation in observations
    }

    assert ObservationType.AIR_TEMPERATURE in types
    assert ObservationType.AIR_HUMIDITY in types
    assert ObservationType.RAINFALL in types
    assert ObservationType.WIND_SPEED in types

    assert all(
        observation.source == ObservationSource.WEATHER_API
        for observation in observations
    )