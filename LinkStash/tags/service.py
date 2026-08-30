
from typing import List
from sqlalchemy.orm import Session
from utils import get_paginated
from tags.models import Tag
class TagService:
    def __init__(self,db:Session) -> None:
        self.db = db

    def create_tag(self,tag:Tag) -> Tag:
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def get_tag(self,tag_id:int) -> Tag:
        return self.db.query(Tag).filter(Tag.id == tag_id).first()
        
    def get_all_tags(self,filters:dict = {}) -> List[Tag]:
        return get_paginated(self.db,Tag,filters=filters,page=1,page_size=10)

    def update_tag(self,tag_id:int,tag:Tag) -> Tag:
        self.db.query(Tag).filter(Tag.id == tag_id).update(tag.model_dump())
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete_tag(self,tag_id:int) -> Tag:
        self.db.query(Tag).filter(Tag.id == tag_id).delete()
        self.db.commit()
        return True
        
        