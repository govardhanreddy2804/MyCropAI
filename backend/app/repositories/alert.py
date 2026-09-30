from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert


def create_alert(
    db: Session,
    alert: Alert,
) -> Alert:
    db.add(alert)
    db.flush()

    return alert


def get_alert_by_id(
    db: Session,
    alert_id: UUID,
) -> Alert | None:
    statement = select(Alert).where(
        Alert.id == alert_id
    )

    return db.scalar(statement)


def get_alerts_by_farm(
    db: Session,
    farm_id: UUID,
) -> list[Alert]:
    statement = (
        select(Alert)
        .where(
            Alert.farm_id == farm_id
        )
        .order_by(
            Alert.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def get_active_alert_by_deduplication_key(
    db: Session,
    deduplication_key: str,
) -> Alert | None:
    statement = (
        select(Alert)
        .where(
            Alert.deduplication_key
            == deduplication_key,
            Alert.status.notin_(["expired"]),
        )
        .order_by(
            Alert.created_at.desc()
        )
    )

    return db.scalar(statement)


def update_alert(
    db: Session,
    alert: Alert,
    updates: dict,
) -> Alert:
    for field, value in updates.items():
        setattr(
            alert,
            field,
            value,
        )

    db.flush()

    return alert