from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import ObservationSource, ObservationType


class AgriculturalObservation(Base):
    __tablename__ = "agricultural_observations"

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

    observation_type: Mapped[ObservationType] = mapped_column(
        Enum(ObservationType),
        nullable=False,
        index=True,
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    source: Mapped[ObservationSource] = mapped_column(
        Enum(ObservationSource),
        nullable=False,
        index=True,
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    field: Mapped["Field"] = relationship(
    back_populates="observations",
    )