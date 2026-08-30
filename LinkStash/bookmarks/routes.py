from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from bookmarks.schema import Bookmark, BookmarkCreate, BookmarkTagAttach, BookmarkUpdate
from bookmarks.service import BookmarkService
from database.session import get_db
from user.models import User
from user.utils import get_current_user
from utils import Paginated, list_params, query_filters

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
    pagination: dict = Depends(list_params),
    tag: str | None = Query(None, description="Filter by tag name"),
    q: str | None = Query(None, description="Search title or url"),
):
    return bookmark_service.get_all_bookmarks(
        current_user,
        filters={**query_filters(request), **pagination["filters"]},
        page=pagination["page"],
        page_size=pagination["page_size"],
        sort_dir=pagination["sort_dir"],
        tag=tag,
        q=q,
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


@router.patch("/{bookmark_id}", response_model=Bookmark)
def patch_bookmark(
    bookmark_id: int,
    bookmark: BookmarkUpdate,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return bookmark_service.patch_bookmark(bookmark_id, bookmark, current_user)


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bookmark(
    bookmark_id: int,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    bookmark_service.delete_bookmark(bookmark_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{bookmark_id}/tags", response_model=Bookmark)
def attach_tag(
    bookmark_id: int,
    body: BookmarkTagAttach,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return bookmark_service.attach_tag(bookmark_id, body.tag_id, current_user)


@router.delete("/{bookmark_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def detach_tag(
    bookmark_id: int,
    tag_id: int,
    bookmark_service: BookmarkService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    bookmark_service.detach_tag(bookmark_id, tag_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
