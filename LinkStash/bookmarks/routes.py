from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from  database.session import get_db
from  bookmarks.service import BookmarkService
from typing import List
from bookmarks.schema import Bookmark
from user.utils import get_current_user
router = APIRouter(prefix="/bookmarks", tags=["bookmarks"],dependencies=[Depends(get_current_user)])
def get_service(session:Session = Depends(get_db)) -> BookmarkService:
    return BookmarkService(session)
@router.post("/", )
def create_bookmark(bookmark, bookmark_service: BookmarkService = Depends(get_service)):
            return bookmark_service.create_bookmark(bookmark)

@router.get("/", response_model=List[Bookmark])
def get_bookmarks(bookmark_service: BookmarkService = Depends(get_service)):
            return bookmark_service.get_all_bookmarks()

@router.get("/{bookmark_id}", response_model=Bookmark)
def get_bookmark(bookmark_id: int, bookmark_service: BookmarkService = Depends(get_service)):
    return bookmark_service.get_bookmark(bookmark_id)

@router.put("/{bookmark_id}", response_model=Bookmark)
def update_bookmark(bookmark_id: int, bookmark:      Bookmark, bookmark_service: BookmarkService = Depends(get_service)):
    return bookmark_service.update_bookmark(bookmark_id, bookmark)

@router.delete("/{bookmark_id}", response_model=bool)
def delete_bookmark(bookmark_id: int, bookmark_service: BookmarkService = Depends(get_service)):
    return bookmark_service.delete_bookmark(bookmark_id)