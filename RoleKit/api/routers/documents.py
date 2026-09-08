"""
routers/documents.py — the gated resource.

Each verb has its own code. Hiding a button in React is not enough:
a raw fetch with a viewer token still hits these Depends and gets 403.

    GET    documents:read
    POST   documents:write   (create)
    PATCH  documents:edit    (update)
    DELETE documents:delete  → 204
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from api.database import get_db
from api.deps import require_permission
from api.models import Document, User
from api.schemas import DocumentCreate, DocumentOut, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(
    _: User = Depends(require_permission("documents:read")),
    db: Session = Depends(get_db),
):
    return db.query(Document).order_by(Document.id).all()


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: int,
    _: User = Depends(require_permission("documents:read")),
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    body: DocumentCreate,
    user: User = Depends(require_permission("documents:write")),
    db: Session = Depends(get_db),
):
    doc = Document(title=body.title, body=body.body, owner_id=user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.patch("/{document_id}", response_model=DocumentOut)
def update_document(
    document_id: int,
    body: DocumentUpdate,
    _: User = Depends(require_permission("documents:edit")),
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if body.title is not None:
        doc.title = body.title
    if body.body is not None:
        doc.body = body.body
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    _: User = Depends(require_permission("documents:delete")),
    db: Session = Depends(get_db),
):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(doc)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
