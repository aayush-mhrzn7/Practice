from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from database.session import get_db
from tags.schema import Tag
from tags.service import TagService
from user.models import User
from user.utils import get_current_user
from utils import Paginated, list_params, query_filters

router = APIRouter(prefix="/tags", tags=["tags"], dependencies=[Depends(get_current_user)])


def get_service(session: Session = Depends(get_db)) -> TagService:
    return TagService(session)


@router.post("/", response_model=Tag)
def create_tag(
    tag: Tag,
    tag_service: TagService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return tag_service.create_tag(tag, current_user)


@router.get("/", response_model=Paginated[Tag])
def get_tags(
    request: Request,
    tag_service: TagService = Depends(get_service),
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(list_params),
):
    return tag_service.get_all_tags(
        current_user,
        filters={**query_filters(request), **pagination["filters"]},
        page=pagination["page"],
        page_size=pagination["page_size"],
        sort_dir=pagination["sort_dir"],
    )


@router.get("/{tag_id}", response_model=Tag)
def get_tag(
    tag_id: int,
    tag_service: TagService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return tag_service.get_tag(tag_id, current_user)


@router.put("/{tag_id}", response_model=Tag)
def update_tag(
    tag_id: int,
    tag: Tag,
    tag_service: TagService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return tag_service.update_tag(tag_id, tag, current_user)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    tag_service: TagService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    tag_service.delete_tag(tag_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
