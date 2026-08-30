from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from user.utils import get_current_user
from  database.session import get_db
from  tags.service import TagService
from typing import List
from tags.schema import Tag
router = APIRouter(prefix="/tags", tags=["tags"],dependencies=[Depends(get_current_user)])
def get_service(session:Session = Depends(get_db)) -> TagService:
    return TagService(session)
@router.post("/", )
def create_tag(tag, tag_service: TagService = Depends(get_service)):
    return tag_service.create_tag(tag)

@router.get("/", response_model=List[Tag])
def get_tags(tag_service: TagService = Depends(get_service)):
    return tag_service.get_all_tags()

@router.get("/{tag_id}", response_model=Tag)
def get_tag(tag_id: int, tag_service: TagService = Depends(get_service)):
    return tag_service.get_tag(tag_id)

@router.put("/{tag_id}", response_model=Tag)
def update_tag(tag_id: int, tag: Tag, tag_service: TagService = Depends(get_service)):
    return tag_service.update_tag(tag_id, tag)

@router.delete("/{tag_id}", response_model=bool)
def delete_tag(tag_id: int, tag_service: TagService = Depends(get_service)):
    return tag_service.delete_tag(tag_id)