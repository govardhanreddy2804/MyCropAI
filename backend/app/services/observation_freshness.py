from dataclasses import dataclass

from app.models.enums import ObservationType


@dataclass(frozen=True)
class FreshnessPolicy:
    max_age_hours: float


FRESHNESS_POLICIES: dict[ObservationType, FreshnessPolicy] = {
    ObservationType.SOIL_MOISTURE: FreshnessPolicy(
        max_age_hours=24,
    ),
    ObservationType.SOIL_TEMPERATURE: FreshnessPolicy(
        max_age_hours=24,
    ),
    ObservationType.SOIL_PH: FreshnessPolicy(
        max_age_hours=168,
    ),
    ObservationType.NITROGEN: FreshnessPolicy(
        max_age_hours=168,
    ),
    ObservationType.PHOSPHORUS: FreshnessPolicy(
        max_age_hours=168,
    ),
    ObservationType.POTASSIUM: FreshnessPolicy(
        max_age_hours=168,
    ),
    ObservationType.AIR_TEMPERATURE: FreshnessPolicy(
        max_age_hours=6,
    ),
    ObservationType.AIR_HUMIDITY: FreshnessPolicy(
        max_age_hours=6,
    ),
    ObservationType.RAINFALL: FreshnessPolicy(
        max_age_hours=24,
    ),
    ObservationType.WIND_SPEED: FreshnessPolicy(
        max_age_hours=6,
    ),
    ObservationType.LIGHT_INTENSITY: FreshnessPolicy(
        max_age_hours=12,
    ),
}


def get_freshness_policy(
    observation_type: ObservationType,
) -> FreshnessPolicy:
    return FRESHNESS_POLICIES.get(
        observation_type,
        FreshnessPolicy(max_age_hours=24),
    )