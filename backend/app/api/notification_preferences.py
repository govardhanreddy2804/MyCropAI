from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.enums import AlertType, NotificationChannel
from app.models.user import User
from app.schemas.notification_preference import (
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)
from app.services.notification_preference import (
    get_user_preferences,
    set_user_preference,
)


router = APIRouter(
    prefix="/api/v1/notification-preferences",
    tags=["Notification Preferences"],
)


@router.get(
    "",
    response_model=list[NotificationPreferenceResponse],
)
def get_notification_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_preferences(
        db=db,
        user_id=current_user.id,
    )


@router.put(
    "/{alert_type}/{channel}",
    response_model=NotificationPreferenceResponse,
    status_code=status.HTTP_200_OK,
)
def update_notification_preference(
    alert_type: AlertType,
    channel: NotificationChannel,
    payload: NotificationPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preference = set_user_preference(
        db=db,
        user_id=current_user.id,
        alert_type=alert_type,
        channel=channel,
        enabled=payload.enabled,
    )

    db.commit()
    db.refresh(preference)

    return preference