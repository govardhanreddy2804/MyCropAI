from dataclasses import dataclass
from enum import Enum


class IrrigationDecision(str, Enum):
    WATER_NOW = "water_now"
    NO_IRRIGATION_NEEDED = "no_irrigation_needed"
    WAIT_AFTER_RAIN = "wait_after_rain"
    INSUFFICIENT_DATA = "insufficient_data"
    WATER_SOON = "water_soon"


@dataclass(frozen=True)
class IrrigationDecisionResult:
    decision: IrrigationDecision
    title: str
    message: str
    priority: str


def determine_irrigation_decision(
    *,
    irrigation_required: bool,
    water_required_liters: float,
    soil_moisture: float | None,
    rainfall_mm: float | None,
    confidence: float,
) -> IrrigationDecisionResult:

    if soil_moisture is None:
        return IrrigationDecisionResult(
            decision=IrrigationDecision.INSUFFICIENT_DATA,
            title="More data needed",
            message=(
                "Current soil moisture data is unavailable. "
                "Add a soil moisture observation before making "
                "an irrigation decision."
            ),
            priority="medium",
        )

    recent_rainfall = rainfall_mm or 0.0

    if not irrigation_required:
        return IrrigationDecisionResult(
            decision=IrrigationDecision.NO_IRRIGATION_NEEDED,
            title="No irrigation needed",
            message=(
                "Current soil moisture is sufficient for the "
                "current irrigation assessment."
            ),
            priority="low",
        )

    if recent_rainfall >= 5.0:
        return IrrigationDecisionResult(
            decision=IrrigationDecision.WAIT_AFTER_RAIN,
            title="Wait before irrigating",
            message=(
                f"Recent rainfall of {recent_rainfall:.1f} mm "
                "has been detected. Reassess soil moisture "
                "before irrigating."
            ),
            priority="medium",
        )

    if confidence < 0.50:
        return IrrigationDecisionResult(
            decision=IrrigationDecision.INSUFFICIENT_DATA,
            title="Low-confidence irrigation recommendation",
            message=(
                "Irrigation may be required, but the available "
                "data is not sufficiently reliable."
            ),
            priority="medium",
        )

    if water_required_liters > 0:
        return IrrigationDecisionResult(
            decision=IrrigationDecision.WATER_NOW,
            title="Irrigation recommended",
            message=(
                "Current conditions indicate that irrigation "
                "is recommended."
            ),
            priority="high",
        )

    return IrrigationDecisionResult(
        decision=IrrigationDecision.WATER_SOON,
        title="Irrigation may be needed soon",
        message=(
            "Current conditions indicate that irrigation "
            "should be reviewed again soon."
        ),
        priority="medium",
    )