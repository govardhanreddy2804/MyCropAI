from datetime import datetime, timezone
from uuid import uuid4

from app.models.alert import Alert
from app.models.crop import Crop
from app.models.enums import (
    AlertPriority,
    AlertStatus,
    AlertType,
    CropStatus,
)
from app.models.farm import Farm
from app.models.field import Field


def create_test_farm(
    db_session,
    authenticated_client,
):
    farm = Farm(
        id=uuid4(),
        owner_id=authenticated_client.user.id,
        name="Alert Test Farm",
        location="Hyderabad",
        area=5.0,
        soil_type="loamy",
    )

    db_session.add(farm)
    db_session.commit()

    return farm


def create_test_field(
    db_session,
    farm,
):
    field = Field(
        id=uuid4(),
        farm_id=farm.id,
        name="Alert Test Field",
        area=2.0,
        soil_type="loamy",
        location="Hyderabad",
    )

    db_session.add(field)
    db_session.commit()

    return field


def create_test_crop(
    db_session,
    field,
):
    crop = Crop(
        id=uuid4(),
        field_id=field.id,
        crop_type="maize",
        variety=None,
        planting_date=datetime.now(timezone.utc).date(),
        expected_harvest_date=None,
        status=CropStatus.ACTIVE,
    )

    db_session.add(crop)
    db_session.commit()

    return crop


def create_test_alert(
    db_session,
    farm,
    field,
    crop,
):
    alert = Alert(
        id=uuid4(),
        farm_id=farm.id,
        field_id=field.id,
        crop_id=crop.id,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        status=AlertStatus.UNREAD,
        title="Irrigation Required",
        message=(
            "Soil moisture is below the recommended "
            "threshold. Irrigation is recommended."
        ),
        deduplication_key=f"irrigation-{uuid4()}",
        created_at=datetime.now(timezone.utc),
        expires_at=None,
        read_at=None,
        acknowledged_at=None,
    )

    db_session.add(alert)
    db_session.commit()

    return alert


def test_list_alerts(
    authenticated_client,
    db_session,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    field = create_test_field(
        db_session,
        farm,
    )

    crop = create_test_crop(
        db_session,
        field,
    )

    alert = create_test_alert(
        db_session,
        farm,
        field,
        crop,
    )

    response = authenticated_client.get(
        f"/api/v1/farms/{farm.id}/alerts"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    alert_data = next(
        item
        for item in data
        if item["id"] == str(alert.id)
    )

    assert alert_data["farm_id"] == str(farm.id)
    assert alert_data["field_id"] == str(field.id)
    assert alert_data["crop_id"] == str(crop.id)

    assert alert_data["alert_type"] == "irrigation"
    assert alert_data["priority"] == "high"
    assert alert_data["status"] == "unread"

    assert alert_data["title"] == "Irrigation Required"


def test_mark_alert_as_read(
    authenticated_client,
    db_session,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    field = create_test_field(
        db_session,
        farm,
    )

    crop = create_test_crop(
        db_session,
        field,
    )

    alert = create_test_alert(
        db_session,
        farm,
        field,
        crop,
    )

    response = authenticated_client.patch(
        f"/api/v1/farms/{farm.id}/alerts/{alert.id}/read"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(alert.id)
    assert data["status"] == "read"


def test_acknowledge_alert(
    authenticated_client,
    db_session,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    field = create_test_field(
        db_session,
        farm,
    )

    crop = create_test_crop(
        db_session,
        field,
    )

    alert = create_test_alert(
        db_session,
        farm,
        field,
        crop,
    )

    response = authenticated_client.patch(
        f"/api/v1/farms/{farm.id}/alerts/{alert.id}/acknowledge"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(alert.id)
    assert data["status"] == "acknowledged"


def test_farmer_cannot_access_another_farm_alerts(
    authenticated_client,
    second_authenticated_client,
    db_session,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    field = create_test_field(
        db_session,
        farm,
    )

    crop = create_test_crop(
        db_session,
        field,
    )

    alert = create_test_alert(
        db_session,
        farm,
        field,
        crop,
    )

    response = second_authenticated_client.get(
        f"/api/v1/farms/{farm.id}/alerts"
    )

    assert response.status_code == 403


def test_marking_nonexistent_alert_as_read_returns_404(
    authenticated_client,
    db_session,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    nonexistent_alert_id = uuid4()

    response = authenticated_client.patch(
        f"/api/v1/farms/{farm.id}/alerts/"
        f"{nonexistent_alert_id}/read"
    )

    assert response.status_code == 404


def test_acknowledging_nonexistent_alert_returns_404(
    authenticated_client,
    db_session,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    nonexistent_alert_id = uuid4()

    response = authenticated_client.patch(
        f"/api/v1/farms/{farm.id}/alerts/"
        f"{nonexistent_alert_id}/acknowledge"
    )

    assert response.status_code == 404