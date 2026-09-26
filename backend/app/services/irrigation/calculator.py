from dataclasses import dataclass

from app.services.irrigation.crop_profile import (
    get_crop_water_profile,
)


@dataclass
class IrrigationCalculation:
    irrigation_required: bool
    water_required_liters: float
    reason: str
    confidence: float


def calculate_irrigation_requirement(
    *,
    field_area_acres: float,
    soil_moisture: float | None,
    rainfall_mm: float | None,
    air_temperature: float | None,
    air_humidity: float | None,
    soil_type: str | None,
    crop_type: str,
) -> IrrigationCalculation:
    """
    Initial transparent irrigation model.

    This is a foundation model, not a scientifically complete
    ET-based irrigation model.
    """

    if field_area_acres <= 0:
        raise ValueError("Field area must be greater than zero")

    # Get crop-specific irrigation profile.
    profile = get_crop_water_profile(crop_type)

    threshold = profile.moisture_threshold
    confidence = profile.base_confidence

    if soil_moisture is None:
        return IrrigationCalculation(
            irrigation_required=False,
            water_required_liters=0,
            reason="Insufficient soil moisture data",
            confidence=0.25,
        )

    # Recent rainfall reduces the immediate irrigation requirement.
    recent_rainfall = rainfall_mm or 0.0

    if soil_moisture >= threshold:
        return IrrigationCalculation(
            irrigation_required=False,
            water_required_liters=0,
            reason=(
                f"Soil moisture ({soil_moisture:.1f}%) is above "
                f"the {threshold:.1f}% irrigation threshold"
            ),
            confidence=round(confidence, 2),
        )

    # Moisture deficit represented as percentage points.
    moisture_deficit = threshold - soil_moisture

    # Initial water-depth estimate.
    #
    # This coefficient is deliberately kept as a model parameter
    # rather than hidden inside the API.
    water_depth_mm = moisture_deficit * 1.0

    # Account for recent rainfall.
    effective_rainfall = min(
        recent_rainfall,
        water_depth_mm,
    )

    net_water_depth_mm = max(
        0.0,
        water_depth_mm - effective_rainfall,
    )

    # 1 mm over 1 acre ≈ 4,046.86 liters.
    liters_per_mm_per_acre = 4046.86

    water_required_liters = (
        net_water_depth_mm
        * field_area_acres
        * liters_per_mm_per_acre
    )

    # Adjust confidence based on available supporting data.
    if rainfall_mm is not None:
        confidence += 0.10

    if soil_type:
        confidence += 0.10

    if air_temperature is not None:
        confidence += 0.05

    if air_humidity is not None:
        confidence += 0.05

    confidence = min(confidence, 0.95)

    reason = (
        f"Soil moisture ({soil_moisture:.1f}%) is below "
        f"the estimated {threshold:.1f}% irrigation threshold "
        f"for {crop_type}"
    )

    if recent_rainfall > 0:
        reason += (
            f"; {recent_rainfall:.1f} mm recent rainfall "
            "was accounted for"
        )

    return IrrigationCalculation(
        irrigation_required=True,
        water_required_liters=round(
            water_required_liters,
            2,
        ),
        reason=reason,
        confidence=round(confidence, 2),
    )