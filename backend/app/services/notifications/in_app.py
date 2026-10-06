from datetime import datetime, timezone

from app.models.enums import NotificationStatus
from app.models.notification import Notification
from app.services.notifications.provider import (
    NotificationProvider,
)


class InAppNotificationProvider(
    NotificationProvider
):

    def send(
        self,
        notification: Notification,
    ) -> Notification:

        now = datetime.now(timezone.utc)

        notification.status = (
            NotificationStatus.DELIVERED
        )

        notification.delivered_at = now

        return notification