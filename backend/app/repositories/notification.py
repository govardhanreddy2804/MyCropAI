from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    NotificationChannel,
)
from app.models.notification import Notification


def create_notification(
    db: Session,
    notification: Notification,
) -> Notification:
    db.add(notification)
    db.flush()

    return notification


def get_notification_by_id(
    db: Session,
    notification_id: UUID,
) -> Notification | None:
    statement = select(Notification).where(Notification.id == notification_id)

    return db.scalar(statement)


def get_notifications_by_user(
    db: Session,
    user_id: UUID,
) -> list[Notification]:
    statement = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )

    return list(db.scalars(statement).all())


def get_notification_for_alert_and_channel(
    db: Session,
    *,
    alert_id: UUID,
    user_id: UUID,
    channel: NotificationChannel,
) -> Notification | None:
    statement = select(Notification).where(
        Notification.alert_id == alert_id,
        Notification.user_id == user_id,
        Notification.channel == channel,
    )

    return db.scalar(statement)


def update_notification(
    db: Session,
    notification: Notification,
    values: dict,
) -> Notification:
    for field, value in values.items():
        setattr(notification, field, value)

    db.flush()

    return notification
