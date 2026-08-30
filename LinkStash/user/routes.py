from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database.session import get_db
from user.models import User
from user.schema import User as UserCreate, UserLogin, UserLoginResponse, UserOut
from user.service import UserService
from user.utils import create_token, get_current_user, hash_password, verify_password
from utils import Paginated, pagination_params, query_filters


def get_service(session: Session = Depends(get_db)) -> UserService:
    return UserService(session)


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserOut)
def signup(
    user: UserCreate,
    service: UserService = Depends(get_service),
):
    if service.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    user.password = hash_password(user.password)
    return service.create_user(user)


@router.post("/login", response_model=UserLoginResponse)
def login(
    user: UserLogin,
    service: UserService = Depends(get_service),
):
    user_exists = service.get_user_by_email(user.email)
    if not user_exists or not verify_password(user.password, user_exists.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return {
        "access_token": create_token({"sub": str(user_exists.id)}),
        "refresh_token": create_token({"sub": str(user_exists.id)}, ttl=60 * 60 * 24 * 30, type="refresh"),
        "token_type": "Bearer",
    }


@router.get("/", response_model=Paginated[UserOut])
def get_users(
    request: Request,
    service: UserService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(pagination_params),
):
    return service.get_all_users(
        current_user,
        filters=query_filters(request),
        page=pagination["page"],
        page_size=pagination["page_size"],
    )


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    service: UserService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_user(user_id, current_user)
