from fastapi import HTTPException, status


def ensure_farm_owner(
    farm,
    current_user,
):

    if farm.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this farm",
        )

    return farm
