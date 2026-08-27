from fastapi import HTTPException, status

from app.models.enums import UserRole


def can_access_farm(
    current_user,
    farm,
) -> bool:

    if current_user.role == UserRole.ADMIN:
        return True

    return farm.owner_id == current_user.id

def require_farm_access(
    current_user,
    farm,
):
    if not can_access_farm(
        current_user,
        farm,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this farm",
        )

    return farm