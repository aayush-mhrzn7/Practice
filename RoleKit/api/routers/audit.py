from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.deps import require_permission
from api.models import AuditEvent, User
from api.schemas import AuditEventOut

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventOut])
def list_audit(
    _: User = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
):
    return db.query(AuditEvent).order_by(AuditEvent.id.desc()).limit(100).all()


def record(db: Session, actor_id: int, action: str, detail: str) -> None:
    db.add(AuditEvent(actor_id=actor_id, action=action, detail=detail))
