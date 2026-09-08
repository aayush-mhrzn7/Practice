"""
deps.py — who may call this route.

Two different gates
    require_admin         → is_admin flag. Used for /roles and /users.
    require_permission(c) → SQL: user → roles → permission codes. Used for
                            /documents and /audit.

Why this is not inside the JWT
    Login stamps sub only. If admin revokes a role, the next request
    still presents the same token, then this file reloads from SQLite
    and raises 403. That is the whole point of RoleKit.

Why load_permission_codes queries again every time
    Do not cache codes on user.permissions across requests.
    selectinload pulls roles and their permissions in this request's session.

require_permission is a factory
    FastAPI Depends needs a callable with no extra args besides injected
    ones. So require_permission("documents:edit") returns `checker`,
    and checker is what FastAPI actually calls.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from api.auth import get_current_user
from api.database import get_db
from api.models import Role, User


def load_permission_codes(db: Session, user_id: int) -> set[str]:
    """
    Walk user_roles → roles → role_permissions → permission.code.

    Returns a set so "does this user have documents:edit?" is just `in`.
    Empty set if the user id is gone (should not happen after get_current_user).
    """
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
    """Bootstrap gate for managing the matrix. Not a document superuser."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
    return user


def require_permission(code: str):
    """
    Build a Depends that 403s unless `code` is in the user's current SQL set.

    Usage on a route:
        user: User = Depends(require_permission("documents:delete"))

    FastAPI runs get_current_user first (401 if no/bad token), then checker
    (403 if the code is missing). That order means a viewer hitting DELETE
    gets 403 even if the document id does not exist — we never leak 404
    before the permission check.
    """

    def checker(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if code not in load_permission_codes(db, user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="no permission")
        return user

    return checker
