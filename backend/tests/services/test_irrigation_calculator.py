from app.services.irrigation.calculator import (
    calculate_irrigation_requirement,
)


def test_irrigation_not_required_when_soil_is_wet():
    result = calculate_irrigation_requirement(
        field_area_acres=2.0,
        crop_type="maize",
        soil_moisture=60.0,
        rainfall_mm=0.0,
        air_temperature=30.0,
        air_humidity=60.0,
        soil_type="loamy",
    )

    assert result.irrigation_required is False
    assert result.water_required_liters == 0


def test_irrigation_required_when_soil_is_dry():
    result = calculate_irrigation_requirement(
        field_area_acres=1.0,
        crop_type="maize",
        soil_moisture=20.0,
        rainfall_mm=0.0,
        air_temperature=32.0,
        air_humidity=45.0,
        soil_type="loamy",
    )

    assert result.irrigation_required is True
    assert result.water_required_liters > 0


def test_rainfall_reduces_required_water():
    without_rain = calculate_irrigation_requirement(
        field_area_acres=1.0,
        crop_type="maize",
        soil_moisture=20.0,
        rainfall_mm=0.0,
        air_temperature=32.0,
        air_humidity=45.0,
        soil_type="loamy",
    )

    with_rain = calculate_irrigation_requirement(
        field_area_acres=1.0,
        crop_type="maize",
        soil_moisture=20.0,
        rainfall_mm=10.0,
        air_temperature=32.0,
        air_humidity=45.0,
        soil_type="loamy",
    )

    assert (
        with_rain.water_required_liters
        < without_rain.water_required_liters
    )


def test_missing_soil_moisture_does_not_trigger_irrigation():
    result = calculate_irrigation_requirement(
        field_area_acres=1.0,
        crop_type="maize",
        soil_moisture=None,
        rainfall_mm=0.0,
        air_temperature=32.0,
        air_humidity=45.0,
        soil_type="loamy",
    )

    assert result.irrigation_required is False
    assert result.water_required_liters == 0