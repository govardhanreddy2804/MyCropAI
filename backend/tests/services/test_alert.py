from datetime import datetime, timezone

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
from app.services.alert import (
    acknowledge_alert,
    create_or_get_alert,
    mark_alert_read,
)


def create_test_farm(db_session, authenticated_client):
    farm = Farm(
        owner_id=authenticated_client.user.id,
        name="Alert Service Test Farm",
        location="Hyderabad",
        area=5.0,
        soil_type="loamy",
    )

    db_session.add(farm)
    db_session.commit()
    db_session.refresh(farm)

    return farm


def create_test_field(db_session, farm):
    field = Field(
        farm_id=farm.id,
        name="Alert Service Test Field",
        area=2.0,
        soil_type="loamy",
        location="Hyderabad",
    )

    db_session.add(field)
    db_session.commit()
    db_session.refresh(field)

    return field


def create_test_crop(db_session, field):
    crop = Crop(
        field_id=field.id,
        crop_type="maize",
        variety=None,
        planting_date=datetime.now(timezone.utc).date(),
        expected_harvest_date=None,
        status=CropStatus.ACTIVE,
    )

    db_session.add(crop)
    db_session.commit()
    db_session.refresh(crop)

    return crop


def test_create_alert(
    db_session,
    authenticated_client,
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

    alert = create_or_get_alert(
        db=db_session,
        farm_id=farm.id,
        field_id=field.id,
        crop_id=crop.id,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        title="Irrigation recommended",
        message="Water is recommended.",
        deduplication_key="test-irrigation-alert",
    )

    assert alert.id is not None
    assert alert.status == AlertStatus.UNREAD
    assert alert.alert_type == AlertType.IRRIGATION
    assert alert.priority == AlertPriority.HIGH


def test_duplicate_alert_is_not_created(
    db_session,
    authenticated_client,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    first = create_or_get_alert(
        db=db_session,
        farm_id=farm.id,
        field_id=None,
        crop_id=None,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        title="Irrigation recommended",
        message="Water is recommended.",
        deduplication_key="duplicate-test",
    )

    second = create_or_get_alert(
        db=db_session,
        farm_id=farm.id,
        field_id=None,
        crop_id=None,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        title="Irrigation recommended",
        message="Water is recommended.",
        deduplication_key="duplicate-test",
    )

    assert first.id == second.id


def test_mark_alert_read(
    db_session,
    authenticated_client,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    alert = create_or_get_alert(
        db=db_session,
        farm_id=farm.id,
        field_id=None,
        crop_id=None,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        title="Test",
        message="Test alert",
        deduplication_key="read-test",
    )

    result = mark_alert_read(
        db_session,
        alert,
    )

    assert result.status == AlertStatus.READ
    assert result.read_at is not None


def test_acknowledge_alert(
    db_session,
    authenticated_client,
):
    farm = create_test_farm(
        db_session,
        authenticated_client,
    )

    alert = create_or_get_alert(
        db=db_session,
        farm_id=farm.id,
        field_id=None,
        crop_id=None,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        title="Test",
        message="Test alert",
        deduplication_key="ack-test",
    )

    result = acknowledge_alert(
        db_session,
        alert,
    )

    assert result.status == AlertStatus.ACKNOWLEDGED
    assert result.acknowledged_at is not None