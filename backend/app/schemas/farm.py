from pydantic import BaseModel, Field

from uuid import UUID
from pydantic import BaseModel, ConfigDict


class FarmCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    location: str = Field(
        min_length=1,
        max_length=255,
    )

    area: float = Field(
        gt=0,
    )

    soil_type: str | None = Field(
        default=None,
        max_length=100,
    )


class FarmResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    owner_id: UUID
    name: str
    location: str
    area: float
    soil_type: str | None