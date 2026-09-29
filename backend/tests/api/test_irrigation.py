from datetime import datetime, timezone
from uuid import uuid4

from app.models.crop import Crop
from app.models.enums import (
    CropStatus,
    ObservationSource,
    ObservationType,
)
from app.models.farm import Farm
from app.models.field import Field
from app.models.observation import AgriculturalObservation

def create_test_farm_field_crop(
    db_session,
    authenticated_client,
    *,
    field_area=1.0,
    soil_type="loamy",
    crop_type="maize",
):
    """
    Create a farm -> field -> crop hierarchy for irrigation tests.

    Returns:
        farm, field, crop
    """

    user_id = authenticated_client.user.id

    farm = Farm(
        owner_id=user_id,
        name="Irrigation Test Farm",
        location="Hyderabad",
        area=5.0,
    )

    db_session.add(farm)
    db_session.flush()

    field = Field(
        farm_id=farm.id,
        name="Irrigation Test Field",
        area=field_area,
        soil_type=soil_type,
    )

    db_session.add(field)
    db_session.flush()

    crop = Crop(
        field_id=field.id,
        crop_type=crop_type,
        planting_date=datetime.now(timezone.utc).date(),
        status=CropStatus.ACTIVE,
    )

    db_session.add(crop)
    db_session.commit()

    return farm, field, crop


def add_observation(
    db_session,
    *,
    field_id,
    observation_type,
    value,
    unit,
    source=ObservationSource.MANUAL,
    confidence=0.9,
):
    observation = AgriculturalObservation(
        id=uuid4(),
        field_id=field_id,
        observation_type=observation_type,
        value=value,
        unit=unit,
        source=source,
        observed_at=datetime.now(timezone.utc),
        confidence=confidence,
    )

    db_session.add(observation)
    db_session.commit()

    return observation


def test_irrigation_recommended(
    authenticated_client,
    db_session,
):
    """
    Dry soil + no recent rainfall should produce
    a water_now recommendation.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.SOIL_MOISTURE,
        value=20,
        unit="percent",
        source=ObservationSource.MANUAL,
        confidence=0.9,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.RAINFALL,
        value=0,
        unit="mm",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.AIR_TEMPERATURE,
        value=32,
        unit="celsius",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.AIR_HUMIDITY,
        value=45,
        unit="percent",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["field_id"] == str(field.id)
    assert data["crop_id"] == str(crop.id)

    assert data["irrigation_required"] is True
    assert data["decision"] == "water_now"
    assert data["priority"] == "high"

    assert data["water_required_liters"] > 0

    assert data["soil_moisture"] == 20
    assert data["rainfall_mm"] == 0
    assert data["air_temperature"] == 32
    assert data["air_humidity"] == 45

    assert data["recommended_duration_minutes"] is None

    assert data["confidence"] > 0


def test_no_irrigation_needed_when_soil_moisture_is_sufficient(
    authenticated_client,
    db_session,
):
    """
    Soil moisture above the crop threshold should
    result in no irrigation being recommended.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.SOIL_MOISTURE,
        value=60,
        unit="percent",
        source=ObservationSource.MANUAL,
        confidence=0.9,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.RAINFALL,
        value=0,
        unit="mm",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["irrigation_required"] is False
    assert data["decision"] == "no_irrigation_needed"
    assert data["priority"] == "low"

    assert data["water_required_liters"] == 0


def test_wait_after_recent_rainfall(
    authenticated_client,
    db_session,
):
    """
    If irrigation would otherwise be required but recent
    rainfall is significant, the system should recommend
    waiting and reassessing.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.SOIL_MOISTURE,
        value=25,
        unit="percent",
        source=ObservationSource.MANUAL,
        confidence=0.9,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.RAINFALL,
        value=10,
        unit="mm",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["irrigation_required"] is True
    assert data["decision"] == "wait_after_rain"
    assert data["priority"] == "medium"

    assert data["rainfall_mm"] == 10


def test_insufficient_data_when_soil_moisture_is_missing(
    authenticated_client,
    db_session,
):
    """
    Without soil moisture data, the system must not
    invent an irrigation requirement.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.RAINFALL,
        value=0,
        unit="mm",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.AIR_TEMPERATURE,
        value=32,
        unit="celsius",
        source=ObservationSource.WEATHER_API,
        confidence=0.8,
    )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["irrigation_required"] is False
    assert data["decision"] == "insufficient_data"

    assert data["water_required_liters"] == 0
    assert data["soil_moisture"] is None


def test_crop_must_belong_to_field(
    authenticated_client,
    db_session,
):
    """
    A crop belonging to another field must not be usable
    for this field's irrigation recommendation.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    other_field = Field(
        id=uuid4(),
        farm_id=farm.id,
        name="Other Field",
        area=1.0,
        soil_type="loamy",
        location="Other Location",
    )

    db_session.add(other_field)
    db_session.flush()

    other_crop = Crop(
        id=uuid4(),
        field_id=other_field.id,
        crop_type="rice",
        variety=None,
        planting_date=datetime.now(timezone.utc).date(),
        expected_harvest_date=None,
        status=CropStatus.ACTIVE,
    )

    db_session.add(other_crop)
    db_session.flush()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(other_crop.id),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Crop not found"


def test_nonexistent_crop_returns_404(
    authenticated_client,
    db_session,
):
    """
    A nonexistent crop ID should return 404.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    nonexistent_crop_id = uuid4()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(nonexistent_crop_id),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Crop not found"


def test_nonexistent_field_returns_404(
    authenticated_client,
    db_session,
):
    """
    A nonexistent field should return 404.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    nonexistent_field_id = uuid4()

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{nonexistent_field_id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Field not found"


def test_nonexistent_farm_returns_404(
    authenticated_client,
    db_session,
):
    """
    A nonexistent farm should return 404.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    nonexistent_farm_id = uuid4()

    response = authenticated_client.get(
        f"/api/v1/farms/{nonexistent_farm_id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found"


def test_other_farmer_cannot_get_irrigation_recommendation(
    authenticated_client,
    second_authenticated_client,
    db_session,
):
    """
    A farmer must not access another farmer's irrigation
    recommendation.
    """

    farm, field, crop = create_test_farm_field_crop(
        db_session,
        authenticated_client,
    )

    add_observation(
        db_session,
        field_id=field.id,
        observation_type=ObservationType.SOIL_MOISTURE,
        value=20,
        unit="percent",
        source=ObservationSource.MANUAL,
        confidence=0.9,
    )

    response = second_authenticated_client.get(
        f"/api/v1/farms/{farm.id}"
        f"/fields/{field.id}"
        f"/irrigation/recommendation",
        params={
            "crop_id": str(crop.id),
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You do not have access to this farm"
    )