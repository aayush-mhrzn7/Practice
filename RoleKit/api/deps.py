from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth import get_current_user
from api.database import get_db
from api.models import Permission, Role, User, role_permissions, user_roles


def load_permission_codes(db: Session, user_id: int) -> set[str]:
    rows = db.execute(
        select(Permission.code)
        .select_from(user_roles)
        .join(Role, Role.id == user_roles.c.role_id)
        .join(role_permissions, role_permissions.c.role_id == Role.id)
        .join(Permission, Permission.id == role_permissions.c.permission_id)
        .where(user_roles.c.user_id == user_id)
    ).all()
    return {row[0] for row in rows}


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no permission",
        )
    return user


def require_permission(code: str):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        codes = load_permission_codes(db, user.id)
        if code not in codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="no permission",
            )
        return user

    return checker
