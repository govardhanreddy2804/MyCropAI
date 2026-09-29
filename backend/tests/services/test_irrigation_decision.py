from app.services.irrigation.decision import (
    IrrigationDecision,
    determine_irrigation_decision,
)


def test_no_irrigation_needed():
    result = determine_irrigation_decision(
        irrigation_required=False,
        water_required_liters=0,
        soil_moisture=60,
        rainfall_mm=0,
        confidence=0.8,
    )

    assert (
        result.decision
        == IrrigationDecision.NO_IRRIGATION_NEEDED
    )


def test_water_now():
    result = determine_irrigation_decision(
        irrigation_required=True,
        water_required_liters=5000,
        soil_moisture=20,
        rainfall_mm=0,
        confidence=0.8,
    )

    assert (
        result.decision
        == IrrigationDecision.WATER_NOW
    )

    assert result.priority == "high"


def test_wait_after_rain():
    result = determine_irrigation_decision(
        irrigation_required=True,
        water_required_liters=5000,
        soil_moisture=25,
        rainfall_mm=10,
        confidence=0.8,
    )

    assert (
        result.decision
        == IrrigationDecision.WAIT_AFTER_RAIN
    )


def test_insufficient_data():
    result = determine_irrigation_decision(
        irrigation_required=False,
        water_required_liters=0,
        soil_moisture=None,
        rainfall_mm=None,
        confidence=0.2,
    )

    assert (
        result.decision
        == IrrigationDecision.INSUFFICIENT_DATA
    )


def test_low_confidence():
    result = determine_irrigation_decision(
        irrigation_required=True,
        water_required_liters=5000,
        soil_moisture=20,
        rainfall_mm=0,
        confidence=0.3,
    )

    assert (
        result.decision
        == IrrigationDecision.INSUFFICIENT_DATA
    )