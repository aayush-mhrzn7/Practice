import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status

load_dotenv()

SECRET = os.getenv("JWT_SECRET", "blogcms-dev-secret-change-me-32b")
ALGO = "HS256"

ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=7)


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_hash(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(data: dict, ttl: timedelta | int) -> str:
    """Sign a JWT. Use for both access tokens and refresh tokens by passing different ttl."""
    expire = datetime.now(timezone.utc) + (
        ttl if isinstance(ttl, timedelta) else timedelta(seconds=ttl)
    )
    payload = {**data, "exp": expire}
    return jwt.encode(payload, SECRET, algorithm=ALGO)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
