from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    NotificationChannel,
    NotificationStatus,
)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    alert_id: UUID

    channel: NotificationChannel
    status: NotificationStatus

    title: str
    message: str

    created_at: datetime
    delivered_at: datetime | None
    read_at: datetime | None
    failure_reason: str | None
