from app.models.enums import (
    AlertPriority,
    AlertType,
    NotificationChannel,
)
from app.services.alert import (
    create_or_get_alert,
)
from app.services.notifications.service import (
    create_alert_notification,
)


def create_irrigation_alert(
    db,
    *,
    farm_id,
    field_id,
    crop_id,
    user_id,
    decision,
):
    if decision.decision.value in {
        "no_irrigation_needed",
        "insufficient_data",
    }:
        return None

    deduplication_key = f"irrigation:{field_id}:{crop_id}:{decision.decision.value}"

    alert = create_or_get_alert(
        db=db,
        farm_id=farm_id,
        field_id=field_id,
        crop_id=crop_id,
        alert_type=AlertType.IRRIGATION,
        priority=AlertPriority(decision.priority),
        title=decision.title,
        message=decision.message,
        deduplication_key=deduplication_key,
    )

    create_alert_notification(
        db=db,
        user_id=user_id,
        alert_id=alert.id,
        channel=NotificationChannel.IN_APP,
    )

    return alert
