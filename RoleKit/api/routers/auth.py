from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.auth import create_access_token, get_current_user, hash_password, verify_password
from api.database import get_db
from api.deps import load_permission_codes
from api.models import User
from api.schemas import TokenOut, UserCreate, UserLogin, UserOut

router = APIRouter(tags=["auth"])


def user_out(db: Session, user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        is_admin=user.is_admin,
        permissions=sorted(load_permission_codes(db, user.id)),
    )


@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: UserCreate, db: Session = Depends(get_db)):
    # First account becomes admin so you do not need a seed script.
    first_user = db.query(User).count() == 0
    user = User(
        email=body.email.strip().lower(),
        password_hash=hash_password(body.password),
        is_admin=first_user,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    db.refresh(user)
    return user_out(db, user)


@router.post("/auth/login", response_model=TokenOut)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.strip().lower()).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenOut(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_out(db, user)
