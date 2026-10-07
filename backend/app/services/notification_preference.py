from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import AlertType, NotificationChannel
from app.models.notification_preference import NotificationPreference
from app.repositories.notification_preference import (
    create_preference,
    get_preference,
    get_preferences_by_user,
    update_preference,
)

DEFAULT_CHANNEL_SETTINGS = {
    NotificationChannel.IN_APP: True,
    NotificationChannel.EMAIL: False,
    NotificationChannel.PUSH: False,
    NotificationChannel.SMS: False,
}


def get_user_preferences(
    db: Session,
    user_id: UUID,
) -> list[NotificationPreference]:
    return get_preferences_by_user(
        db=db,
        user_id=user_id,
    )


def set_user_preference(
    db: Session,
    *,
    user_id: UUID,
    alert_type: AlertType,
    channel: NotificationChannel,
    enabled: bool,
) -> NotificationPreference:
    preference = get_preference(
        db=db,
        user_id=user_id,
        alert_type=alert_type,
        channel=channel,
    )

    if preference is None:
        return create_preference(
            db=db,
            user_id=user_id,
            alert_type=alert_type,
            channel=channel,
            enabled=enabled,
        )

    return update_preference(
        db=db,
        preference=preference,
        enabled=enabled,
    )


def is_channel_enabled(
    db: Session,
    *,
    user_id: UUID,
    alert_type: AlertType,
    channel: NotificationChannel,
) -> bool:
    preference = get_preference(
        db=db,
        user_id=user_id,
        alert_type=alert_type,
        channel=channel,
    )

    if preference is not None:
        return preference.enabled

    return DEFAULT_CHANNEL_SETTINGS[channel]
