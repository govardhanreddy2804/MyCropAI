from app.models.enums import (
    AlertPriority,
    AlertType,
)

from app.services.alert import create_or_get_alert


def create_irrigation_alert(
    db,
    *,
    farm_id,
    field_id,
    crop_id,
    decision,
):
    if decision.decision.value == "no_irrigation_needed":
        return None

    if decision.decision.value == "insufficient_data":
        return None

    deduplication_key = (
        f"irrigation:"
        f"{field_id}:"
        f"{crop_id}:"
        f"{decision.decision.value}"
    )

    priority = AlertPriority(
        decision.priority
    )

    return create_or_get_alert(
        db=db,
        farm_id=farm_id,
        field_id=field_id,
        crop_id=crop_id,
        alert_type=AlertType.IRRIGATION,
        priority=priority,
        title=decision.title,
        message=decision.message,
        deduplication_key=deduplication_key,
    )