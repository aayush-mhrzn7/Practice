"""
auth.py — passwords and JWT.

The token payload is only:
    { "sub": "<user id>", "exp": <unix time> }

It does not contain roles, permissions, or is_admin.
If you put those in the token, revoke would wait until expiry.

get_current_user
    1. Read Authorization: Bearer
    2. Decode sub
    3. Load that User from SQL
    Missing/expired/unknown id → 401, not 403.
    403 is for "we know who you are, you lack a code" (see deps.py).
"""

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.database import get_db
from api.models import User

load_dotenv()

SECRET = os.getenv("JWT_SECRET", "rolekit-dev-secret")
ALGO = "HS256"
TOKEN_TTL = timedelta(hours=8)
# auto_error=False so we can return our own 401 body instead of FastAPI's default.
bearer = HTTPBearer(auto_error=False)


def hash_password(plain: str) -> str:
    """bcrypt hash, stored as a utf-8 string in users.password_hash."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """Sign a JWT whose only identity claim is sub = user id."""
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + TOKEN_TTL,
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_token(token: str) -> int:
    """Return user id from sub, or raise 401."""
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGO])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return int(sub)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency used by every protected route (directly or via deps.py).

    Does not load roles here. Roles are loaded again in require_permission
    so we never accidentally reuse a cached permission set on the User object.
    """
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = decode_token(creds.credentials)
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user
