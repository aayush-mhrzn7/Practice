from fastapi import APIRouter, Depends

from api.auth import get_current_user
from api.models import PERMISSION_GROUPS, User
from api.schemas import PermissionGroupOut, PermissionItem

router = APIRouter(tags=["permissions"])


@router.get("/permissions", response_model=list[PermissionGroupOut])
def permission_catalog(_: User = Depends(get_current_user)):
    return [
        PermissionGroupOut(
            key=group["key"],
            label=group["label"],
            permissions=[
                PermissionItem(code=code, label=label) for code, label in group["items"]
            ],
        )
        for group in PERMISSION_GROUPS
    ]
