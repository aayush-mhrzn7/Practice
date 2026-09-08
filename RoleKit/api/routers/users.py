"""
routers/users.py — grant and revoke.

Grant  POST   /users/{id}/roles/{role_id}  → insert user_roles
Revoke DELETE /users/{id}/roles/{role_id}  → delete that row

The user's JWT does not change. The next documents/audit request
reloads codes in deps.py and 403s if the revoked role owned them.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from api.database import get_db
from api.deps import require_admin
from api.models import Role, User
from api.routers.audit import add_audit
from api.schemas import RoleBrief, UserListOut

router = APIRouter(prefix="/users", tags=["users"])


def user_list_out(user: User) -> UserListOut:
    return UserListOut(
        id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        roles=[RoleBrief.model_validate(role) for role in user.roles],
    )


@router.get("", response_model=list[UserListOut])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).options(selectinload(User.roles)).order_by(User.email).all()
    return [user_list_out(user) for user in users]


@router.post("/{user_id}/roles/{role_id}", response_model=UserListOut)
def grant_role(
    user_id: int,
    role_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).options(selectinload(User.roles)).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role not in user.roles:
        user.roles.append(role)
        add_audit(db, admin.id, "grant", f"{user.email} + {role.name}")
        db.commit()
        db.refresh(user)
    return user_list_out(user)


@router.delete("/{user_id}/roles/{role_id}", response_model=UserListOut)
def revoke_role(
    user_id: int,
    role_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.query(User).options(selectinload(User.roles)).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    role = next((r for r in user.roles if r.id == role_id), None)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not assigned")
    user.roles.remove(role)
    add_audit(db, admin.id, "revoke", f"{user.email} - {role.name}")
    db.commit()
    db.refresh(user)
    return user_list_out(user)
