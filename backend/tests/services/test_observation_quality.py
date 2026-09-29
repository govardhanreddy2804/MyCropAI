from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models.enums import (
    ObservationSource,
    ObservationType,
)
from app.models.observation import AgriculturalObservation
from app.services.observation_quality import (
    classify_observation_quality,
    get_observation_age_hours,
    is_observation_fresh,
)
from app.services.observation_quality import (
    ObservationQuality,
)


def make_observation(
    *,
    observation_type=ObservationType.SOIL_MOISTURE,
    observed_at=None,
    confidence=0.9,
):
    return AgriculturalObservation(
        id=uuid4(),
        field_id=uuid4(),
        observation_type=observation_type,
        value=25,
        unit="percent",
        source=ObservationSource.MANUAL,
        observed_at=(
            observed_at
            or datetime.now(timezone.utc)
        ),
        confidence=confidence,
    )


def test_fresh_observation():
    now = datetime.now(timezone.utc)

    observation = make_observation(
        observed_at=now - timedelta(hours=2),
    )

    assert is_observation_fresh(
        observation,
        now=now,
    )


def test_stale_soil_moisture():
    now = datetime.now(timezone.utc)

    observation = make_observation(
        observed_at=now - timedelta(hours=48),
    )

    assert not is_observation_fresh(
        observation,
        now=now,
    )


def test_observation_age():
    now = datetime.now(timezone.utc)

    observation = make_observation(
        observed_at=now - timedelta(hours=5),
    )

    age = get_observation_age_hours(
        observation,
        now=now,
    )

    assert 4.99 < age < 5.01


def test_low_confidence_classification():
    now = datetime.now(timezone.utc)

    observation = make_observation(
        observed_at=now - timedelta(hours=1),
        confidence=0.2,
    )

    result = classify_observation_quality(
        observation,
        now=now,
    )

    assert result == ObservationQuality.FRESH_LOW_CONFIDENCE


def test_stale_classification():
    now = datetime.now(timezone.utc)

    observation = make_observation(
        observed_at=now - timedelta(hours=48),
        confidence=0.9,
    )

    result = classify_observation_quality(
        observation,
        now=now,
    )

    assert result == ObservationQuality.STALE