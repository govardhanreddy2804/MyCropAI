from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import (
    AlertPriority,
    AlertStatus,
    AlertType,
)

if TYPE_CHECKING:
    from app.models.crop import Crop
    from app.models.farm import Farm
    from app.models.field import Field


class Alert(Base):
    __tablename__ = "alerts"

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

    field_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "fields.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    crop_id: Mapped[UUID | None] = mapped_column(
        ForeignKey(
            "crops.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    alert_type: Mapped[AlertType] = mapped_column(
        Enum(AlertType),
        nullable=False,
        index=True,
    )

    priority: Mapped[AlertPriority] = mapped_column(
        Enum(AlertPriority),
        nullable=False,
        index=True,
    )

    status: Mapped[AlertStatus] = mapped_column(
        Enum(AlertStatus),
        nullable=False,
        default=AlertStatus.UNREAD,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    deduplication_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    farm: Mapped["Farm"] = relationship(
        "Farm",
        back_populates="alerts",
    )

    field: Mapped["Field | None"] = relationship(
        "Field",
        back_populates="alerts",
    )

    crop: Mapped["Crop | None"] = relationship(
        "Crop",
        back_populates="alerts",
    )