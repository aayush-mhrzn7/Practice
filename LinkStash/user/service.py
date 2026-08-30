from fastapi import HTTPException
from sqlalchemy.orm import Session

from user.models import User
from user.schema import User as UserSchema
from utils import get_paginated


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_user(self, user: UserSchema) -> User:
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

    def get_user(self, user_id: int, current_user: User) -> User:
        if user_id != current_user.id:
            raise HTTPException(status_code=404, detail="User not found")
        return current_user

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_all_users(
        self,
        current_user: User,
        filters: dict | None = None,
        page: int = 1,
        page_size: int = 10,
        sort_dir: str = "desc",
    ):
        return get_paginated(
            self.db,
            User,
            filters=filters,
            page=page,
            page_size=page_size,
            sort_dir=sort_dir,
            query=self.db.query(User).filter(User.id == current_user.id),
        )
