from sqlalchemy.orm import Session
from typing import List
from utils import get_paginated
from user.models import User
from user.schema import User as UserSchema

class UserService:
    def __init__(self,db:Session) -> None:
        self.db = db

    def create_user(self,user:UserSchema) -> User:
        db_user = User(
            email=user.email,
            password=user.password,
            name=user.name,
            bio=user.bio,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user(self,user_id:int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self,email:str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def get_all_users(self,filters:dict = {}) -> List[User]:
        return get_paginated(self.db,User,filters=filters,page=1,page_size=10)