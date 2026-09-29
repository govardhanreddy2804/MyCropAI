from collections import defaultdict
from datetime import datetime, timezone

from app.models.observation import AgriculturalObservation
from app.services.observation_freshness import (
    get_freshness_policy,
)
from app.services.observation_priority import (
    get_source_priority,
)


def get_observation_age_hours(
    observation: AgriculturalObservation,
    now: datetime,
) -> float:
    observed_at = observation.observed_at

    if observed_at.tzinfo is None:
        observed_at = observed_at.replace(
            tzinfo=timezone.utc,
        )

    return max(
        0.0,
        (now - observed_at).total_seconds() / 3600,
    )


def is_fresh(
    observation: AgriculturalObservation,
    now: datetime,
) -> bool:
    age_hours = get_observation_age_hours(
        observation,
        now,
    )

    policy = get_freshness_policy(
        observation.observation_type,
    )

    return age_hours <= policy.max_age_hours


def observation_score(
    observation: AgriculturalObservation,
    *,
    now: datetime | None = None,
) -> float:

    if now is None:
        now = datetime.now(timezone.utc)

    age_hours = get_observation_age_hours(
        observation,
        now,
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

    freshness_score = 100 / (
        1 + age_hours / 24
    )

    return (
        source_score * 0.60
        + freshness_score * 0.25
        + confidence_score * 100 * 0.15
    )


def resolve_best_observation(
    observations: list[AgriculturalObservation],
):
    if not observations:
        return None

    now = datetime.now(timezone.utc)

    fresh_observations = [
        observation
        for observation in observations
        if is_fresh(observation, now)
    ]

    candidates = (
        fresh_observations
        if fresh_observations
        else observations
    )

    return max(
        candidates,
        key=lambda observation: observation_score(
            observation,
            now=now,
        ),
    )


def resolve_best_observations(
    observations: list[AgriculturalObservation],
):
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

def resolve_safe_current_observations(
    observations: list[AgriculturalObservation],
):
    grouped = defaultdict(list)

    for observation in observations:
        grouped[
            observation.observation_type
        ].append(observation)

    resolved = {}
    now = datetime.now(timezone.utc)

    for observation_type, items in grouped.items():

        fresh_items = [
            observation
            for observation in items
            if is_fresh(observation, now)
            and (
                observation.confidence is None
                or observation.confidence >= 0.50
            )
        ]

        if not fresh_items:
            continue

        best = max(
            fresh_items,
            key=lambda observation: observation_score(
                observation,
                now=now,
            ),
        )

        resolved[observation_type] = best

    return resolved