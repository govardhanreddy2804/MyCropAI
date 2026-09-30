from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.crop import Crop
    from app.models.farm import Farm
    from app.models.observation import AgriculturalObservation


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    farm_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "farms.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    area: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    soil_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    farm: Mapped["Farm"] = relationship(
        "Farm",
        back_populates="fields",
    )

    crops: Mapped[list["Crop"]] = relationship(
        "Crop",
        back_populates="field",
        cascade="all, delete-orphan",
    )

    observations: Mapped[list["AgriculturalObservation"]] = relationship(
        "AgriculturalObservation",
        back_populates="field",
        cascade="all, delete-orphan",
    )

    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="field",
        cascade="all, delete-orphan",
    )