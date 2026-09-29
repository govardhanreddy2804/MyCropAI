from dataclasses import dataclass


@dataclass(frozen=True)
class IrrigationSafetyResult:
    safe_to_recommend: bool
    data_quality: str
    message: str

def assess_irrigation_data_quality(
    *,
    soil_moisture_available: bool,
    rainfall_available: bool,
    temperature_available: bool,
    humidity_available: bool,
) -> IrrigationSafetyResult:

    if not soil_moisture_available:
        return IrrigationSafetyResult(
            safe_to_recommend=False,
            data_quality="insufficient",
            message=(
                "No fresh, sufficiently confident soil "
                "moisture observation is available."
            ),
        )

    if not rainfall_available:
        return IrrigationSafetyResult(
            safe_to_recommend=True,
            data_quality="limited",
            message=(
                "Soil moisture is available, but recent "
                "rainfall data is unavailable."
            ),
        )

    if (
        not temperature_available
        or not humidity_available
    ):
        return IrrigationSafetyResult(
            safe_to_recommend=True,
            data_quality="limited",
            message=(
                "Soil moisture and rainfall are available, "
                "but some weather observations are missing."
            ),
        )

    return IrrigationSafetyResult(
        safe_to_recommend=True,
        data_quality="good",
        message=(
            "Current soil and weather observations are "
            "fresh enough for this recommendation."
        ),
    )