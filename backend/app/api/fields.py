from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

from app.models.user import User

from app.policies.farm_policy import require_farm_access

from app.repositories.farm import get_farm_by_id
from app.repositories.field import get_field_by_id

from app.schemas.field import (
    FieldCreate,
    FieldResponse,
    FieldUpdate,
)

from app.services.field_service import (
    create_farm_field,
    delete_farm_field,
    get_farm_fields,
    update_farm_field,
)


router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/fields",
    tags=["Fields"],
)

@router.post(
    "",
    response_model=FieldResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_field_endpoint(
    farm_id: UUID,
    request: FieldCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    return create_farm_field(
        db=db,
        farm_id=farm_id,
        name=request.name,
        area=request.area,
        soil_type=request.soil_type,
        location=request.location,
    )


@router.get(
    "",
    response_model=list[FieldResponse],
)
def list_fields(
    farm_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    return get_farm_fields(
        db,
        farm_id,
    )

@router.get(
    "/{field_id}",
    response_model=FieldResponse,
)
def get_field(
    farm_id: UUID,
    field_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None or field.farm_id != farm_id:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    return field

@router.put(
    "/{field_id}",
    response_model=FieldResponse,
)
def update_field_endpoint(
    farm_id: UUID,
    field_id: UUID,
    request: FieldUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None or field.farm_id != farm_id:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    values = request.model_dump(
        exclude_unset=True
    )

    return update_farm_field(
        db=db,
        field=field,
        values=values,
    )

@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_field_endpoint(
    farm_id: UUID,
    field_id: UUID,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    farm = get_farm_by_id(
        db,
        farm_id,
    )

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    require_farm_access(
        current_user,
        farm,
    )

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None or field.farm_id != farm_id:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    delete_farm_field(
        db=db,
        field=field,
    )

    return None