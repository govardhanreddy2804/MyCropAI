from datetime import date
from uuid import uuid4

from app.models.crop import Crop
from app.models.enums import (
    AlertPriority,
    AlertType,
    CropStatus,
    NotificationChannel,
    NotificationStatus,
)
from app.models.farm import Farm
from app.models.field import Field
from app.services.alert import create_or_get_alert
from app.services.notifications.service import (
    create_alert_notification,
    mark_notification_read,
)


def create_test_alert(
    db_session,
    authenticated_client,
):
    user_id = authenticated_client.user.id

    farm = Farm(
        id=uuid4(),
        owner_id=user_id,
        name="Notification Test Farm",
        location="Hyderabad",
        area=10.0,
        soil_type="Loamy",
    )

    db_session.add(farm)
    db_session.flush()

    field = Field(
        id=uuid4(),
        farm_id=farm.id,
        name="Notification Test Field",
        area=5.0,
        soil_type="Loamy",
        location="Hyderabad",
        latitude=17.3850,
        longitude=78.4867,
    )

    db_session.add(field)
    db_session.flush()

    crop = Crop(
        id=uuid4(),
        field_id=field.id,
        crop_type="Rice",
        variety="Basmati",
        planting_date=date.today(),
        expected_harvest_date=None,
        status=CropStatus.ACTIVE,
    )

    db_session.add(crop)
    db_session.flush()

    alert = create_or_get_alert(
        db=db_session,
        farm_id=farm.id,
        field_id=field.id,
        crop_id=crop.id,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        title="Irrigation recommended",
        message="Water is recommended.",
        deduplication_key=f"test-{uuid4()}",
    )

    db_session.commit()

    return alert


def test_create_alert_notification(
    db_session,
    authenticated_client,
):
    alert = create_test_alert(
        db_session,
        authenticated_client,
    )

    notification = create_alert_notification(
        db=db_session,
        user_id=authenticated_client.user.id,
        alert_id=alert.id,
        channel=NotificationChannel.IN_APP,
    )

    db_session.commit()

    assert notification is not None
    assert str(notification.user_id) == authenticated_client.user.id
    assert notification.alert_id == alert.id
    assert notification.channel == NotificationChannel.IN_APP

    # InAppNotificationProvider changes PENDING -> DELIVERED
    assert notification.status == NotificationStatus.DELIVERED
    assert notification.delivered_at is not None


def test_notification_is_not_duplicated(
    db_session,
    authenticated_client,
):
    alert = create_test_alert(
        db_session,
        authenticated_client,
    )

    first = create_alert_notification(
        db=db_session,
        user_id=authenticated_client.user.id,
        alert_id=alert.id,
        channel=NotificationChannel.IN_APP,
    )

    second = create_alert_notification(
        db=db_session,
        user_id=authenticated_client.user.id,
        alert_id=alert.id,
        channel=NotificationChannel.IN_APP,
    )

    db_session.commit()

    assert first.id == second.id


def test_mark_notification_read(
    db_session,
    authenticated_client,
):
    alert = create_test_alert(
        db_session,
        authenticated_client,
    )

    notification = create_alert_notification(
        db=db_session,
        user_id=authenticated_client.user.id,
        alert_id=alert.id,
        channel=NotificationChannel.IN_APP,
    )

    db_session.commit()

    updated = mark_notification_read(
        db=db_session,
        notification=notification,
    )

    db_session.commit()

    assert updated.status == NotificationStatus.READ
    assert updated.read_at is not None