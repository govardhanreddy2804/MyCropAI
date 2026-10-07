from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import AlertType, NotificationChannel


class NotificationPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    alert_type: AlertType
    channel: NotificationChannel
    enabled: bool


class NotificationPreferenceUpdate(BaseModel):
    enabled: bool
