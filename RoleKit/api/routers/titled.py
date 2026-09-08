from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.deps import require_permission
from api.models import User
from api.schemas import TitledCreate, TitledOut, TitledUpdate


def make_titled_router(
    prefix: str,
    model,
    read: str,
    write: str,
    edit: str,
    delete: str,
    missing: str,
):
    router = APIRouter(prefix=f"/{prefix}", tags=[prefix])

    @router.get("", response_model=list[TitledOut])
    def list_items(
        _: User = Depends(require_permission(read)),
        db: Session = Depends(get_db),
    ):
        return db.query(model).order_by(model.id).all()

    @router.get("/{item_id}", response_model=TitledOut)
    def get_item(
        item_id: int,
        _: User = Depends(require_permission(read)),
        db: Session = Depends(get_db),
    ):
        item = db.get(model, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=missing)
        return item

    @router.post("", response_model=TitledOut, status_code=status.HTTP_201_CREATED)
    def create_item(
        body: TitledCreate,
        user: User = Depends(require_permission(write)),
        db: Session = Depends(get_db),
    ):
        item = model(title=body.title, body=body.body, owner_id=user.id)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @router.patch("/{item_id}", response_model=TitledOut)
    def update_item(
        item_id: int,
        body: TitledUpdate,
        _: User = Depends(require_permission(edit)),
        db: Session = Depends(get_db),
    ):
        item = db.get(model, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=missing)
        if body.title is not None:
            item.title = body.title
        if body.body is not None:
            item.body = body.body
        db.commit()
        db.refresh(item)
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(
        item_id: int,
        _: User = Depends(require_permission(delete)),
        db: Session = Depends(get_db),
    ):
        item = db.get(model, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=missing)
        db.delete(item)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
