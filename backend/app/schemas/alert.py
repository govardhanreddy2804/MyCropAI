from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    AlertPriority,
    AlertStatus,
    AlertType,
)


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID

    farm_id: UUID
    field_id: UUID | None
    crop_id: UUID | None

    alert_type: AlertType
    priority: AlertPriority
    status: AlertStatus

    title: str
    message: str

    created_at: datetime
    expires_at: datetime | None

    read_at: datetime | None
    acknowledged_at: datetime | None