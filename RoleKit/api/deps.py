from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from api.auth import get_current_user
from api.database import get_db
from api.models import Role, User


def load_permission_codes(db: Session, user_id: int) -> set[str]:
    user = (
        db.query(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .filter(User.id == user_id)
        .first()
    )
    if user is None:
        return set()
    codes: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            codes.add(perm.code)
    return codes


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
    return user


def require_permission(code: str):
    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if code not in load_permission_codes(db, user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
        return user

    return checker
