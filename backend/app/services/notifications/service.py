from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import (
    NotificationChannel,
    NotificationStatus,
)
from app.models.notification import Notification
from app.repositories.alert import get_alert_by_id
from app.repositories.notification import (
    create_notification,
    get_notification_for_alert_and_channel,
    update_notification,
)
from app.services.notifications.in_app import (
    InAppNotificationProvider,
)


def create_alert_notification(
    db: Session,
    *,
    user_id: UUID,
    alert_id: UUID,
    channel: NotificationChannel,
) -> Notification:

    existing = (
        get_notification_for_alert_and_channel(
            db,
            alert_id=alert_id,
            user_id=user_id,
            channel=channel,
        )
    )

    if existing is not None:
        return existing

    alert = get_alert_by_id(
        db,
        alert_id,
    )

    if alert is None:
        raise ValueError(
            "Alert not found"
        )

    notification = Notification(
        user_id=user_id,
        alert_id=alert.id,
        channel=channel,
        status=NotificationStatus.PENDING,
        title=alert.title,
        message=alert.message,
        created_at=datetime.now(timezone.utc),
    )

    create_notification(
        db,
        notification,
    )

    if channel == NotificationChannel.IN_APP:
        provider = InAppNotificationProvider()

        notification = provider.send(
            notification,
        )

    return notification


def mark_notification_read(
    db: Session,
    notification: Notification,
) -> Notification:

    if notification.status == (
        NotificationStatus.READ
    ):
        return notification

    notification.status = NotificationStatus.READ
    notification.read_at = datetime.now(
        timezone.utc
    )

    return update_notification(
        db,
        notification,
        {},
    )