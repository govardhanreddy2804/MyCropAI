import uuid
from datetime import datetime

from app.models.notification_preference import NotificationPreference
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

from sqlalchemy import Enum

from app.models.enums import UserRole

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.notification import Notification
    from app.models.notification_preference import NotificationPreference


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.FARMER,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notification_preferences: Mapped[list["NotificationPreference"]] = relationship(
        "NotificationPreference",
        back_populates="user",
        cascade="all, delete-orphan",
    )
