"""keep documents + audit only

Revision ID: 003_simplify
Revises: 002_more_resources
Create Date: 2026-09-08
"""

from typing import Sequence, Union

from alembic import op

revision: str = "003_simplify"
down_revision: Union[str, None] = "002_more_resources"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

KEEP = (
    "documents:read",
    "documents:write",
    "documents:edit",
    "documents:delete",
    "audit:read",
)


def upgrade() -> None:
    op.execute("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code NOT IN ('documents:read', 'documents:write', 'documents:edit', 'documents:delete', 'audit:read'))")
    op.execute("DELETE FROM permissions WHERE code NOT IN ('documents:read', 'documents:write', 'documents:edit', 'documents:delete', 'audit:read')")
    op.drop_table("settings")
    op.drop_table("announcements")
    op.drop_table("notes")


def downgrade() -> None:
    pass
