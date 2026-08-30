from sqlalchemy.orm import Session
from bookmarks.models import Bookmark
from  utils import get_paginated
from typing import List
class BookmarkService:
    def __init__(self,db:Session) -> None:
        self.db = db

    def create_bookmark(self,bookmark:Bookmark) -> Bookmark:
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark
        
    def get_bookmark(self,bookmark_id:int) -> Bookmark:
        return self.db.query(Bookmark).filter(Bookmark.id == bookmark_id).first()
        
    def get_all_bookmarks(self,filters:dict = {}) -> List[Bookmark]:
        return get_paginated(self.db,Bookmark,filters=filters,page=1,page_size=10)
        
    def update_bookmark(self,bookmark_id:int,bookmark:Bookmark) -> Bookmark:
        self.db.query(Bookmark).filter(Bookmark.id == bookmark_id).update(bookmark.model_dump())
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark

    def delete_bookmark(self,bookmark_id:int) -> bool:
        self.db.query(Bookmark).filter(Bookmark.id == bookmark_id).delete()
        self.db.commit()
        return True