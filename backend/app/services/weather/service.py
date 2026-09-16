from datetime import datetime

from sqlalchemy.orm import Session

from app.models.enums import ObservationSource, ObservationType
from app.models.observation import AgriculturalObservation
from app.repositories.observation import create_observation
from app.services.weather.provider import WeatherProvider


def ingest_current_weather(
    db: Session,
    field_id,
    provider: WeatherProvider,
    latitude: float,
    longitude: float,
) -> list[AgriculturalObservation]:

    weather = provider.get_current_weather(
        latitude=latitude,
        longitude=longitude,
    )

    observations: list[AgriculturalObservation] = []

    values = [
        (
            ObservationType.AIR_TEMPERATURE,
            weather.air_temperature,
            weather.temperature_unit,
        ),
        (
            ObservationType.AIR_HUMIDITY,
            weather.air_humidity,
            weather.humidity_unit,
        ),
        (
            ObservationType.RAINFALL,
            weather.rainfall,
            weather.rainfall_unit,
        ),
        (
            ObservationType.WIND_SPEED,
            weather.wind_speed,
            weather.wind_speed_unit,
        ),
    ]

    for observation_type, value, unit in values:
        if value is None:
            continue

        observation = AgriculturalObservation(
            field_id=field_id,
            observation_type=observation_type,
            value=value,
            unit=unit,
            source=ObservationSource.WEATHER_API,
            observed_at=weather.observed_at,
            confidence=0.8,
        )

        create_observation(db, observation)
        observations.append(observation)

    return observations