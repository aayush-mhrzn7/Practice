from fastapi import APIRouter, Depends
from user.utils import get_current_user
from database.session import get_db
from user.service import UserService
from user.schema import User
from sqlalchemy.orm import Session
from typing import List

def get_service(
    session: Session = Depends(get_db)
) -> UserService:
    return UserService(session)

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", response_model=User)
def signup(user: User, service: UserService = Depends(get_service)):
    return service.create_user(user)

@router.post("/login", response_model=User)
def login(user: User, service: UserService = Depends(get_service)):
    return service.login(user)

@router.get("/", response_model=List[User])
def get_users(service: UserService = Depends(get_service), user = Depends(get_current_user)):
    return service.get_all_users()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, service: UserService = Depends(get_service), user = Depends(get_current_user)):
    return service.get_user(user_id)