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
    resolve_best_observations,
)

from app.services.irrigation.decision import (
    determine_irrigation_decision,
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

    best = resolve_best_observations(observations)

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

        "reason": calculation.reason,
        "confidence": calculation.confidence,
        "calculated_at": datetime.now(timezone.utc),
    }