from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.models.enums import CropStatus


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    field_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "fields.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    crop_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    variety: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    planting_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    expected_harvest_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    status: Mapped[CropStatus] = mapped_column(
        Enum(CropStatus),
        nullable=False,
        default=CropStatus.PLANNED,
    )