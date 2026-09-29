from datetime import datetime, timezone
from enum import Enum

from app.models.observation import AgriculturalObservation
from app.services.observation_freshness import (
    get_freshness_policy,
)


def get_observation_age_hours(
    observation: AgriculturalObservation,
    *,
    now: datetime | None = None,
) -> float:
    if now is None:
        now = datetime.now(timezone.utc)

    observed_at = observation.observed_at

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc,
        )

    return max(
        0.0,
        (now - observed_at).total_seconds() / 3600,
    )


def is_observation_fresh(
    observation: AgriculturalObservation,
    *,
    now: datetime | None = None,
) -> bool:
    age_hours = get_observation_age_hours(
        observation,
        now=now,
    )

    policy = get_freshness_policy(
        observation.observation_type,
    )

    return age_hours <= policy.max_age_hours


def is_confidence_acceptable(
    observation: AgriculturalObservation,
    minimum_confidence: float = 0.50,
) -> bool:
    confidence = (
        observation.confidence
        if observation.confidence is not None
        else 0.50
    )

    return confidence >= minimum_confidence


class ObservationQuality(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    LOW_CONFIDENCE = "low_confidence"
    FRESH_LOW_CONFIDENCE = "fresh_low_confidence"


def classify_observation_quality(
    observation: AgriculturalObservation,
    *,
    now: datetime | None = None,
) -> ObservationQuality:

    fresh = is_observation_fresh(
        observation,
        now=now,
    )

    confidence_ok = is_confidence_acceptable(
        observation,
    )

    if fresh and confidence_ok:
        return ObservationQuality.FRESH

    if not fresh and confidence_ok:
        return ObservationQuality.STALE

    if fresh and not confidence_ok:
        return ObservationQuality.FRESH_LOW_CONFIDENCE

    return ObservationQuality.LOW_CONFIDENCE