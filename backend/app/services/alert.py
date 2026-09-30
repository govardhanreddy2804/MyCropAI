from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.enums import (
    AlertPriority,
    AlertStatus,
    AlertType,
)
from app.repositories.alert import (
    create_alert,
    get_active_alert_by_deduplication_key,
    get_alert_by_id,
    get_alerts_by_farm,
    update_alert,
)


def create_or_get_alert(
    db: Session,
    *,
    farm_id: UUID,
    field_id: UUID | None,
    crop_id: UUID | None,
    alert_type: AlertType,
    priority: AlertPriority,
    title: str,
    message: str,
    deduplication_key: str,
    expiration_hours: int = 24,
) -> Alert:

    existing = get_active_alert_by_deduplication_key(
        db,
        deduplication_key,
    )

    if existing is not None:
        return existing

    now = datetime.now(timezone.utc)

    alert = Alert(
        farm_id=farm_id,
        field_id=field_id,
        crop_id=crop_id,
        alert_type=alert_type,
        priority=priority,
        status=AlertStatus.UNREAD,
        title=title,
        message=message,
        deduplication_key=deduplication_key,
        created_at=now,
        expires_at=now + timedelta(
            hours=expiration_hours
        ),
    )

    return create_alert(db, alert)


def list_farm_alerts(
    db: Session,
    farm_id: UUID,
) -> list[Alert]:
    return get_alerts_by_farm(
        db,
        farm_id,
    )


def mark_alert_read(
    db: Session,
    alert: Alert,
) -> Alert:

    if alert.status == AlertStatus.EXPIRED:
        return alert

    now = datetime.now(timezone.utc)

    return update_alert(
        db,
        alert,
        {
            "status": AlertStatus.READ,
            "read_at": now,
        },
    )


def acknowledge_alert(
    db: Session,
    alert: Alert,
) -> Alert:

    if alert.status == AlertStatus.EXPIRED:
        return alert

    now = datetime.now(timezone.utc)

    return update_alert(
        db,
        alert,
        {
            "status": AlertStatus.ACKNOWLEDGED,
            "acknowledged_at": now,
        },
    )

def expire_alert_if_needed(
    db: Session,
    alert: Alert,
) -> Alert:

    if (
        alert.expires_at is not None
        and alert.expires_at
        <= datetime.now(timezone.utc)
        and alert.status != AlertStatus.ACKNOWLEDGED
    ):
        update_alert(
            db,
            alert,
            {
                "status": AlertStatus.EXPIRED,
            },
        )

    return alert

def list_farm_alerts(
    db: Session,
    farm_id: UUID,
) -> list[Alert]:

    alerts = get_alerts_by_farm(
        db,
        farm_id,
    )

    for alert in alerts:
        expire_alert_if_needed(
            db,
            alert,
        )

    return alerts