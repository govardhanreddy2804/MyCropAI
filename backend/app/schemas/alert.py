from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AlertResponse(BaseModel):
    alert_type: str
    priority: AlertPriority
    title: str
    message: str
    created_at: datetime