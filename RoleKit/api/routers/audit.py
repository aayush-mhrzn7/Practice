"""
routers/audit.py — read the log, and a helper to append a row.

GET /audit needs audit:read (a role code), not is_admin.
An admin with no audit:read still 403s here — same rule as documents.

add_audit is called from roles.py and users.py before commit so the
log row lands in the same transaction as the grant/revoke.
"""

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


def add_audit(db: Session, actor_id: int, action: str, detail: str) -> None:
    """Queue an audit_events insert. Caller must db.commit()."""
    db.add(AuditEvent(actor_id=actor_id, action=action, detail=detail))
