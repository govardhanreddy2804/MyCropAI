from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.enums import (
    ObservationSource,
    ObservationType,
)
from app.models.observation import AgriculturalObservation
from app.services.observation_resolver import (
    resolve_safe_current_observations,
)


def make_observation(
    *,
    source,
    observed_at,
    value,
    confidence=0.9,
):
    return AgriculturalObservation(
        id=uuid4(),
        field_id=uuid4(),
        observation_type=ObservationType.SOIL_MOISTURE,
        value=value,
        unit="percent",
        source=source,
        observed_at=observed_at,
        confidence=confidence,
    )


def test_fresh_observation_beats_stale_high_priority_sensor():
    now = datetime.now(timezone.utc)

    stale_sensor = make_observation(
        source=ObservationSource.IOT_SENSOR,
        observed_at=now - timedelta(hours=48),
        value=15,
        confidence=0.95,
    )

    fresh_manual = make_observation(
        source=ObservationSource.MANUAL,
        observed_at=now - timedelta(hours=1),
        value=25,
        confidence=0.90,
    )

    result = resolve_safe_current_observations(
        [
            stale_sensor,
            fresh_manual,
        ]
    )

    best = result[ObservationType.SOIL_MOISTURE]

    assert best.id == fresh_manual.id


def test_stale_only_observation_is_not_returned():
    now = datetime.now(timezone.utc)

    stale_sensor = make_observation(
        source=ObservationSource.IOT_SENSOR,
        observed_at=now - timedelta(hours=48),
        value=15,
        confidence=0.95,
    )

    result = resolve_safe_current_observations(
        [stale_sensor]
    )

    assert ObservationType.SOIL_MOISTURE not in result


def test_low_confidence_observation_is_not_returned():
    now = datetime.now(timezone.utc)

    low_confidence = make_observation(
        source=ObservationSource.MANUAL,
        observed_at=now - timedelta(hours=1),
        value=25,
        confidence=0.20,
    )

    result = resolve_safe_current_observations(
        [low_confidence]
    )

    assert ObservationType.SOIL_MOISTURE not in result