from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.models.user import User
from app.policies.farm_policy import require_farm_access
from app.repositories.alert import get_alert_by_id
from app.repositories.farm import get_farm_by_id
from app.schemas.alert import AlertResponse
from app.services.alert import (
    acknowledge_alert,
    list_farm_alerts,
    mark_alert_read,
)


router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/alerts",
    tags=["Alerts"],
)


def _get_authorized_farm(
    db: Session,
    farm_id: UUID,
    current_user: User,
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    return farm


@router.get(
    "",
    response_model=list[AlertResponse],
)
def get_alerts(
    farm_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_authorized_farm(
        db,
        farm_id,
        current_user,
    )

    alerts = list_farm_alerts(
        db,
        farm_id,
    )

    db.commit()

    return alerts


@router.patch(
    "/{alert_id}/read",
    response_model=AlertResponse,
)
def read_alert(
    farm_id: UUID,
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_authorized_farm(
        db,
        farm_id,
        current_user,
    )

    alert = get_alert_by_id(
        db,
        alert_id,
    )

    if alert is None or alert.farm_id != farm_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert = mark_alert_read(
        db,
        alert,
    )

    db.commit()

    return alert


@router.patch(
    "/{alert_id}/acknowledge",
    response_model=AlertResponse,
)
def acknowledge_alert_endpoint(
    farm_id: UUID,
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_authorized_farm(
        db,
        farm_id,
        current_user,
    )

    alert = get_alert_by_id(
        db,
        alert_id,
    )

    if alert is None or alert.farm_id != farm_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    alert = acknowledge_alert(
        db,
        alert,
    )

    db.commit()

    return alert