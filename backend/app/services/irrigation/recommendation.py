from datetime import datetime, timezone

from app.models.enums import ObservationType
from app.repositories.observation import get_observations_by_field
from app.services.irrigation.calculator import (
    calculate_irrigation_requirement,
)
from app.services.irrigation.crop_profile import (
    get_crop_water_profile,
)
from app.services.observation_resolver import (
    resolve_safe_current_observations,
)
from app.services.observation_quality import (
    ObservationQuality,
    classify_observation_quality,
)
from app.services.irrigation.decision import (
    determine_irrigation_decision,
)

from app.services.irrigation.alert import (
    create_irrigation_alert,
)


def generate_irrigation_recommendation(
    db,
    field,
    crop,
):
    observations = get_observations_by_field(
        db=db,
        field_id=field.id,
    )

    # Only use observations that are considered
    # safe/current enough for an irrigation decision.
    best = resolve_safe_current_observations(
        observations
    )

    soil_moisture_observation = best.get(
        ObservationType.SOIL_MOISTURE
    )

    rainfall_observation = best.get(
        ObservationType.RAINFALL
    )

    temperature_observation = best.get(
        ObservationType.AIR_TEMPERATURE
    )

    humidity_observation = best.get(
        ObservationType.AIR_HUMIDITY
    )

    soil_moisture = (
        soil_moisture_observation.value
        if soil_moisture_observation
        else None
    )

    rainfall = (
        rainfall_observation.value
        if rainfall_observation
        else None
    )

    temperature = (
        temperature_observation.value
        if temperature_observation
        else None
    )

    humidity = (
        humidity_observation.value
        if humidity_observation
        else None
    )

    # Determine the quality of the soil-moisture data.
    # Soil moisture is the most important observation
    # for this irrigation assessment.
    if soil_moisture_observation is None:
        data_quality = "insufficient_data"
        data_quality_message = (
            "Current soil moisture data is unavailable. "
            "Add a recent soil moisture observation before "
            "making an irrigation decision."
        )
    else:
        soil_moisture_quality = classify_observation_quality(
            soil_moisture_observation
        )

        if soil_moisture_quality == ObservationQuality.FRESH:
            data_quality = "fresh"
            data_quality_message = (
                "Current soil moisture data is fresh "
                "and has acceptable confidence."
            )

        elif (
            soil_moisture_quality
            == ObservationQuality.FRESH_LOW_CONFIDENCE
        ):
            data_quality = "fresh_low_confidence"
            data_quality_message = (
                "Current soil moisture data is recent "
                "but has low confidence."
            )

        elif soil_moisture_quality == ObservationQuality.STALE:
            data_quality = "stale"
            data_quality_message = (
                "The available soil moisture data is stale. "
                "A recent observation is recommended."
            )

        else:
            data_quality = "low_confidence"
            data_quality_message = (
                "The available soil moisture data has "
                "low confidence."
            )

    calculation = calculate_irrigation_requirement(
        field_area_acres=field.area,
        crop_type=crop.crop_type,
        soil_moisture=soil_moisture,
        rainfall_mm=rainfall,
        air_temperature=temperature,
        air_humidity=humidity,
        soil_type=field.soil_type,
    )

    decision = determine_irrigation_decision(
        irrigation_required=calculation.irrigation_required,
        water_required_liters=calculation.water_required_liters,
        soil_moisture=soil_moisture,
        rainfall_mm=rainfall,
        confidence=calculation.confidence,
    )

    alert = create_irrigation_alert(
    db=db,
    farm_id=field.farm_id,
    field_id=field.id,
    crop_id=crop.id,
    decision=decision,
)

    return {
        "field_id": field.id,
        "crop_id": crop.id,

        "irrigation_required": (
            calculation.irrigation_required
        ),
        "water_required_liters": (
            calculation.water_required_liters
        ),
        "recommended_duration_minutes": None,

        "soil_moisture": soil_moisture,
        "moisture_threshold": (
            get_crop_water_profile(
                crop.crop_type
            ).moisture_threshold
        ),
        "rainfall_mm": rainfall,
        "air_temperature": temperature,
        "air_humidity": humidity,

        "decision": decision.decision,
        "title": decision.title,
        "message": decision.message,
        "priority": decision.priority,

        "data_quality": data_quality,
        "data_quality_message": data_quality_message,

        "reason": calculation.reason,
        "confidence": calculation.confidence,
        "calculated_at": datetime.now(timezone.utc),
    }