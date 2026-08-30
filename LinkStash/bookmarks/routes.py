from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from bookmarks.schema import Bookmark, BookmarkCreate
from bookmarks.service import BookmarkService
from database.session import get_db
from user.models import User
from user.utils import get_current_user
from utils import Paginated, pagination_params, query_filters

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"], dependencies=[Depends(get_current_user)])


def get_service(session: Session = Depends(get_db)) -> BookmarkService:
    return BookmarkService(session)


@router.post("/", response_model=Bookmark)
def create_bookmark(
    bookmark: BookmarkCreate,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return bookmark_service.create_bookmark(bookmark, current_user)


@router.get("/", response_model=Paginated[Bookmark])
def get_bookmarks(
    request: Request,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(pagination_params),
):
    return bookmark_service.get_all_bookmarks(
        current_user,
        filters=query_filters(request),
        page=pagination["page"],
        page_size=pagination["page_size"],
    )


@router.get("/{bookmark_id}", response_model=Bookmark)
def get_bookmark(
    bookmark_id: int,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return bookmark_service.get_bookmark(bookmark_id, current_user)


@router.put("/{bookmark_id}", response_model=Bookmark)
def update_bookmark(
    bookmark_id: int,
    bookmark: BookmarkCreate,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return bookmark_service.update_bookmark(bookmark_id, bookmark, current_user)


@router.delete("/{bookmark_id}", response_model=bool)
def delete_bookmark(
    bookmark_id: int,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return bookmark_service.delete_bookmark(bookmark_id, current_user)
