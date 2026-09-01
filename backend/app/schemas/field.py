from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FieldCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    area: float = Field(
        gt=0,
    )

    soil_type: str | None = Field(
        default=None,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )


class FieldUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    area: float | None = Field(
        default=None,
        gt=0,
    )

    soil_type: str | None = Field(
        default=None,
        max_length=100,
    )

    location: str | None = Field(
        default=None,
        max_length=255,
    )


class FieldResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    farm_id: UUID
    name: str
    area: float
    soil_type: str | None
    location: str | None