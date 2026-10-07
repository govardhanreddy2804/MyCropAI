from datetime import datetime, timezone
from uuid import uuid4

from app.models.alert import Alert
from app.models.enums import (
    AlertPriority,
    AlertStatus,
    AlertType,
    NotificationChannel,
    NotificationStatus,
)
from app.models.farm import Farm
from app.models.notification import Notification


def create_test_alert(db_session, authenticated_client):
    farm = Farm(
        id=uuid4(),
        owner_id=authenticated_client.user.id,
        name="Notification Test Farm",
        location="Hyderabad",
        area=5.0,
        soil_type="loamy",
    )

    db_session.add(farm)
    db_session.commit()

    alert = Alert(
        id=uuid4(),
        farm_id=farm.id,
        field_id=None,
        crop_id=None,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority.HIGH,
        status=AlertStatus.UNREAD,
        title="Irrigation Required",
        message="Soil moisture is below the recommended threshold.",
        deduplication_key=f"notification-test-{uuid4()}",
        created_at=datetime.now(timezone.utc),
        expires_at=None,
        read_at=None,
        acknowledged_at=None,
    )

    db_session.add(alert)
    db_session.commit()

    return alert


def create_test_notification(
    db_session,
    authenticated_client,
):
    alert = create_test_alert(
        db_session,
        authenticated_client,
    )

    notification = Notification(
        id=uuid4(),
        user_id=authenticated_client.user.id,
        alert_id=alert.id,
        channel=NotificationChannel.IN_APP,
        status=NotificationStatus.PENDING,
        title="Irrigation Required",
        message="Your field needs irrigation.",
        created_at=datetime.now(timezone.utc),
        delivered_at=None,
        read_at=None,
        failure_reason=None,
    )

    db_session.add(notification)
    db_session.commit()

    return notification


def test_list_notifications(
    authenticated_client,
    db_session,
):
    notification = create_test_notification(
        db_session,
        authenticated_client,
    )

    response = authenticated_client.get("/api/v1/notifications")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    notification_data = next(
        item for item in data if item["id"] == str(notification.id)
    )

    assert notification_data["id"] == str(notification.id)
    assert notification_data["user_id"] == str(authenticated_client.user.id)
    assert notification_data["alert_id"] == str(notification.alert_id)
    assert notification_data["channel"] == "in_app"
    assert notification_data["status"] == "pending"
    assert notification_data["title"] == "Irrigation Required"


def test_mark_notification_as_read(
    authenticated_client,
    db_session,
):
    notification = create_test_notification(
        db_session,
        authenticated_client,
    )

    response = authenticated_client.patch(
        f"/api/v1/notifications/{notification.id}/read"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(notification.id)
    assert data["status"] == "read"
    assert data["read_at"] is not None


def test_other_user_cannot_mark_notification_as_read(
    authenticated_client,
    second_authenticated_client,
    db_session,
):
    notification = create_test_notification(
        db_session,
        authenticated_client,
    )

    response = second_authenticated_client.patch(
        f"/api/v1/notifications/{notification.id}/read"
    )

    assert response.status_code == 404
