from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.services.irrigation.decision import IrrigationDecision

class IrrigationRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    field_id: UUID
    crop_id: UUID

    irrigation_required: bool

    water_required_liters: float
    recommended_duration_minutes: float | None

    soil_moisture: float | None
    moisture_threshold: float
    rainfall_mm: float | None
    air_temperature: float | None
    air_humidity: float | None

    decision: IrrigationDecision
    title: str
    message: str
    priority: str

    reason: str
    confidence: float

    calculated_at: datetime