from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.deps import require_permission
from api.models import Setting, User
from api.routers.audit import record
from api.schemas import SettingOut, SettingUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


def _row(db: Session) -> Setting:
    setting = db.get(Setting, 1)
    if setting is None:
        setting = Setting(id=1, workspace_name="RoleKit", banner="")
        db.add(setting)
        db.flush()
    return setting


@router.get("", response_model=SettingOut)
def get_settings(
    _: User = Depends(require_permission("settings:read")),
    db: Session = Depends(get_db),
):
    return _row(db)


@router.patch("", response_model=SettingOut)
def update_settings(
    body: SettingUpdate,
    user: User = Depends(require_permission("settings:edit")),
    db: Session = Depends(get_db),
):
    if body.workspace_name is None and body.banner is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nothing to update")
    setting = _row(db)
    if body.workspace_name is not None:
        setting.workspace_name = body.workspace_name
    if body.banner is not None:
        setting.banner = body.banner
    record(db, user.id, "settings.edit", f"{setting.workspace_name} · {setting.banner}")
    db.commit()
    db.refresh(setting)
    return setting
