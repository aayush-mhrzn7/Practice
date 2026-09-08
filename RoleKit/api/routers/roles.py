from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from api.database import get_db
from api.deps import require_admin
from api.models import PERMISSION_CODES, Permission, Role, User
from api.routers.audit import record
from api.schemas import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


def _role_out(role: Role) -> RoleOut:
    return RoleOut(
        id=role.id,
        name=role.name,
        permissions=sorted(p.code for p in role.permissions),
    )


@router.get("", response_model=list[RoleOut])
def list_roles(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    roles = (
        db.query(Role)
        .options(selectinload(Role.permissions))
        .order_by(Role.name)
        .all()
    )
    return [_role_out(role) for role in roles]


@router.post("", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    body: RoleCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    role = Role(name=body.name.strip())
    db.add(role)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")
    db.refresh(role)
    record(db, admin.id, "role.create", role.name)
    db.commit()
    return _role_out(role)


@router.patch("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    body: RoleUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    role = db.query(Role).options(selectinload(Role.permissions)).filter(Role.id == role_id).first()
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    if body.name is not None:
        role.name = body.name.strip()

    if body.permissions is not None:
        unknown = [code for code in body.permissions if code not in PERMISSION_CODES]
        if unknown:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown permission codes: {unknown}",
            )
        if body.permissions:
            perms = db.query(Permission).filter(Permission.code.in_(body.permissions)).all()
        else:
            perms = []
        role.permissions = perms

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")
    db.refresh(role)
    codes = ", ".join(sorted(p.code for p in role.permissions)) or "none"
    record(db, admin.id, "role.replace", f"{role.name}: {codes}")
    db.commit()
    return _role_out(role)
