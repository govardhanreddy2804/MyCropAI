from datetime import datetime, timezone

from app.models.observation import AgriculturalObservation
from app.services.observation_priority import get_source_priority

from collections import defaultdict
from app.models.enums import ObservationType

def observation_score(
    observation: AgriculturalObservation,
) -> float:
    now = datetime.now(timezone.utc)

    observed_at = observation.observed_at

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc
        )

    age_hours = max(
        0,
        (now - observed_at).total_seconds() / 3600,
    )

    source_score = get_source_priority(
        observation.observation_type,
        observation.source,
    )

    confidence_score = (
        observation.confidence
        if observation.confidence is not None
        else 0.5
    )

    # Freshness decreases gradually as observations become older.
    freshness_score = 100 / (1 + age_hours / 24)

    return (
        source_score * 0.60
        + freshness_score * 0.25
        + confidence_score * 100 * 0.15
    )


def resolve_best_observation(
    observations: list[AgriculturalObservation],
) -> AgriculturalObservation | None:

    if not observations:
        return None

    return max(
        observations,
        key=observation_score,
    )


def resolve_best_observations(
    observations: list[AgriculturalObservation],
) -> dict[
    ObservationType,
    AgriculturalObservation,
]:

    grouped = defaultdict(list)

    for observation in observations:
        grouped[
            observation.observation_type
        ].append(observation)

    resolved = {}

    for observation_type, items in grouped.items():
        best = resolve_best_observation(items)

        if best is not None:
            resolved[observation_type] = best

    return resolved