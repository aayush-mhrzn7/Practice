from fastapi import APIRouter, Depends, HTTPException
from user.utils import create_token, get_current_user, hash_password, verify_password
from database.session import get_db
from user.service import UserService
from user.schema import User, UserLogin, UserLoginResponse, UserOut
from sqlalchemy.orm import Session
from typing import List

def get_service(
    session: Session = Depends(get_db)
) -> UserService:
    return UserService(session)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=UserOut)
def signup(
    user: User,
    # x_csrftoken: str = Header(alias="x-csrftoken"),
    service: UserService = Depends(get_service),
):
    user_exists = service.get_user_by_email(user.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    user.password = hash_password(user.password)
    return service.create_user(user)

@router.post("/login", response_model=UserLoginResponse)
def login(
    user: UserLogin,
    # x_csrftoken: str = Header(alias="x-csrftoken"),
    service: UserService = Depends(get_service),
):
    user_exists = service.get_user_by_email(user.email)
    if not user_exists:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(user.password, user_exists.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_token({"sub": str(user_exists.id)})
    refresh_token = create_token({"sub": str(user_exists.id)}, ttl=60*60*24*30, type="refresh")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }
       

@router.get("/", response_model=List[UserOut])
def get_users(service: UserService = Depends(get_service), user = Depends(get_current_user)):
    return service.get_all_users()

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, service: UserService = Depends(get_service), user = Depends(get_current_user)):
    return service.get_user(user_id)