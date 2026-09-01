from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db

from app.models.user import User

from app.policies.crop_policy import require_crop_access

from app.repositories.crop import get_crop_by_id
from app.repositories.farm import get_farm_by_id
from app.repositories.field import get_field_by_id

from app.schemas.crop import (
    CropCreate,
    CropResponse,
    CropUpdate,
)

from app.services.crop_service import (
    create_field_crop,
    delete_field_crop,
    get_field_crops,
    update_field_crop,
)


router = APIRouter(
    prefix="/api/v1/farms/{farm_id}/fields/{field_id}/crops",
    tags=["Crops"],
)

@router.post(
    "",
    response_model=CropResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_crop_endpoint(
    farm_id: UUID,
    field_id: UUID,
    request: CropCreate,
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

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    require_crop_access(
        current_user,
        farm,
        field,
    )

    return create_field_crop(
        db=db,
        field_id=field_id,
        crop_type=request.crop_type,
        variety=request.variety,
        planting_date=request.planting_date,
        expected_harvest_date=request.expected_harvest_date,
    )

@router.get(
    "",
    response_model=list[CropResponse],
)
def list_crops(
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

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None:
        raise HTTPException(
        status_code=404,
        detail="Field not found",
        )

    require_crop_access(
        current_user,
        farm,
        field,
    )

    return get_field_crops(
        db,
        field_id,
    )

@router.get(
    "/{crop_id}",
    response_model=CropResponse,
)
def get_crop(
    farm_id: UUID,
    field_id: UUID,
    crop_id: UUID,
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

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    crop = get_crop_by_id(
        db,
        crop_id,
    )

    if crop is None:
        raise HTTPException(
            status_code=404,
            detail="Crop not found",
        )

    require_crop_access(
        current_user,
        farm,
        field,
        crop,
    )

    return crop

@router.put(
    "/{crop_id}",
    response_model=CropResponse,
)
def update_crop_endpoint(
    farm_id: UUID,
    field_id: UUID,
    crop_id: UUID,
    request: CropUpdate,
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

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    crop = get_crop_by_id(
        db,
        crop_id,
    )

    if crop is None:
        raise HTTPException(
            status_code=404,
            detail="Crop not found",
        )

    require_crop_access(
        current_user,
        farm,
        field,
        crop,
    )

    values = request.model_dump(
        exclude_unset=True
    )

    return update_field_crop(
        db=db,
        crop=crop,
        values=values,
    )

@router.delete(
    "/{crop_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_crop_endpoint(
    farm_id: UUID,
    field_id: UUID,
    crop_id: UUID,
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

    field = get_field_by_id(
        db,
        field_id,
    )

    if field is None:
        raise HTTPException(
            status_code=404,
            detail="Field not found",
        )

    crop = get_crop_by_id(
        db,
        crop_id,
    )

    if crop is None:
        raise HTTPException(
            status_code=404,
            detail="Crop not found",
        )

    require_crop_access(
        current_user,
        farm,
        field,
        crop,
    )

    delete_field_crop(
        db=db,
        crop=crop,
    )

    return None