from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from RoleKit.database.models import User
from database.session import get_db
import jwt
import bcrypt

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

def generate_token(data:dict) -> str:
    return jwt.encode(data, "this-is-a-secret-key", algorithm="HS256")

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, "this-is-a-secret-key", algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_user(user: UserCreate, db: Session = Depends(get_db)) -> User:
    hashed_password = bcrypt.hashpw(
    user.password.encode(),
    bcrypt.gensalt()
)
    db_user = User(username=user.username, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user) 
    return db_user

def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(
        user.password.encode(),
        db_user.password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = generate_token({"sub": db_user.id})
    return {"access_token": token, "token_type": "Bearer"}