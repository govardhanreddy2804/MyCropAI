from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import CropStatus


class FarmOverviewCrop(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    crop_type: str
    variety: str | None
    status: CropStatus


class FarmOverviewField(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    name: str
    area: float
    soil_type: str | None
    location: str | None
    crops: list[FarmOverviewCrop]


class FarmOverviewResponse(BaseModel):
    id: UUID
    name: str
    location: str
    area: float
    soil_type: str | None
    field_count: int
    crop_count: int
    fields: list[FarmOverviewField]