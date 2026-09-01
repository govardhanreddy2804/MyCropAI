from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CropStatus


class CropCreate(BaseModel):
    crop_type: str = Field(
        min_length=1,
        max_length=100,
    )

    variety: str | None = Field(
        default=None,
        max_length=100,
    )

    planting_date: date

    expected_harvest_date: date | None = None


class CropUpdate(BaseModel):
    crop_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    variety: str | None = Field(
        default=None,
        max_length=100,
    )

    planting_date: date | None = None

    expected_harvest_date: date | None = None

    status: CropStatus | None = None


class CropResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    field_id: UUID
    crop_type: str
    variety: str | None
    planting_date: date
    expected_harvest_date: date | None
    status: CropStatus