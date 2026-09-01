from fastapi import HTTPException, status

from app.policies.farm_policy import can_access_farm


def require_crop_access(
    current_user,
    farm,
    field,
    crop=None,
):
    if not can_access_farm(
        current_user,
        farm,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this crop",
        )

    if field.farm_id != farm.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field not found",
        )

    if crop is not None and crop.field_id != field.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )

    return crop or field