from datetime import datetime, timedelta, timezone

from app.models.enums import ObservationSource, ObservationType
from app.models.observation import AgriculturalObservation
from app.services.observation_resolver import (
    resolve_best_observation,
    resolve_best_observations,
)

from uuid import uuid4

def make_observation(
    observation_type,
    source,
    value,
    hours_old=1,
    confidence=0.9,
):
    return AgriculturalObservation(
        field_id=uuid4(),
        observation_type=observation_type,
        value=value,
        unit="%",
        source=source,
        observed_at=datetime.now(timezone.utc)
        - timedelta(hours=hours_old),
        confidence=confidence,
    )


def test_higher_priority_source_wins():
    sensor = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.IOT_SENSOR,
        25,
    )

    manual = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.MANUAL,
        30,
    )

    result = resolve_best_observation(
        [manual, sensor]
    )

    assert result is sensor


def test_fresh_data_can_beat_stale_high_priority_data():
    stale_sensor = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.IOT_SENSOR,
        20,
        hours_old=240,
    )

    fresh_manual = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.MANUAL,
        30,
        hours_old=1,
    )

    result = resolve_best_observation(
        [stale_sensor, fresh_manual]
    )

    assert result is fresh_manual


def test_confidence_affects_score():
    high_confidence = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.MANUAL,
        25,
        confidence=1.0,
    )

    low_confidence = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.MANUAL,
        30,
        confidence=0.1,
    )

    result = resolve_best_observation(
        [low_confidence, high_confidence]
    )

    assert result is high_confidence


def test_resolves_one_observation_per_type():
    moisture = make_observation(
        ObservationType.SOIL_MOISTURE,
        ObservationSource.MANUAL,
        25,
    )

    humidity = make_observation(
        ObservationType.AIR_HUMIDITY,
        ObservationSource.WEATHER_API,
        65,
    )

    result = resolve_best_observations(
        [moisture, humidity]
    )

    assert len(result) == 2
    assert result[
        ObservationType.SOIL_MOISTURE
    ] is moisture
    assert result[
        ObservationType.AIR_HUMIDITY
    ] is humidity