from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ObservationSource, ObservationType


class ObservationCreate(BaseModel):
    observation_type: ObservationType
    value: float
    unit: str = Field(min_length=1, max_length=30)
    source: ObservationSource = ObservationSource.MANUAL
    observed_at: datetime
    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


class ObservationResponse(BaseModel):
    id: UUID
    field_id: UUID
    observation_type: ObservationType
    value: float
    unit: str
    source: ObservationSource
    observed_at: datetime
    confidence: float | None

    model_config = {
        "from_attributes": True
    }