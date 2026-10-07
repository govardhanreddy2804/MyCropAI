from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import AlertType, NotificationChannel
from app.models.notification_preference import NotificationPreference


def get_preferences_by_user(
    db: Session,
    user_id: UUID,
) -> list[NotificationPreference]:
    stmt = (
        select(NotificationPreference)
        .where(NotificationPreference.user_id == user_id)
        .order_by(
            NotificationPreference.alert_type,
            NotificationPreference.channel,
        )
    )

    return list(db.scalars(stmt).all())


def get_preference(
    db: Session,
    user_id: UUID,
    alert_type: AlertType,
    channel: NotificationChannel,
) -> NotificationPreference | None:
    stmt = select(NotificationPreference).where(
        NotificationPreference.user_id == user_id,
        NotificationPreference.alert_type == alert_type,
        NotificationPreference.channel == channel,
    )

    return db.scalar(stmt)


def create_preference(
    db: Session,
    *,
    user_id: UUID,
    alert_type: AlertType,
    channel: NotificationChannel,
    enabled: bool,
) -> NotificationPreference:
    preference = NotificationPreference(
        user_id=user_id,
        alert_type=alert_type,
        channel=channel,
        enabled=enabled,
    )

    db.add(preference)
    db.flush()

    return preference


def update_preference(
    db: Session,
    preference: NotificationPreference,
    *,
    enabled: bool,
) -> NotificationPreference:
    preference.enabled = enabled

    db.add(preference)
    db.flush()

    return preference
