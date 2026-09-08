"""notes, announcements, audit, settings, extra permission codes

Revision ID: 002_more_resources
Revises: 001_initial
Create Date: 2026-09-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_more_resources"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_CODES = (
    "notes:read",
    "notes:write",
    "notes:edit",
    "notes:delete",
    "announcements:read",
    "announcements:write",
    "announcements:edit",
    "announcements:delete",
    "audit:read",
    "settings:read",
    "settings:edit",
)


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.String(), nullable=False, server_default=""),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_notes_id", "notes", ["id"])

    op.create_table(
        "announcements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("body", sa.String(), nullable=False, server_default=""),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_announcements_id", "announcements", ["id"])

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("detail", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_audit_events_id", "audit_events", ["id"])

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_name", sa.String(), nullable=False, server_default="RoleKit"),
        sa.Column("banner", sa.String(), nullable=False, server_default=""),
    )

    permissions = sa.table("permissions", sa.column("code", sa.String()))
    op.bulk_insert(permissions, [{"code": code} for code in NEW_CODES])

    settings = sa.table(
        "settings",
        sa.column("id", sa.Integer()),
        sa.column("workspace_name", sa.String()),
        sa.column("banner", sa.String()),
    )
    op.bulk_insert(
        settings,
        [
            {
                "id": 1,
                "workspace_name": "RoleKit",
                "banner": "The JWT only carries your user id. Checkboxes never authorize anything.",
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("settings")
    op.drop_table("audit_events")
    op.drop_table("announcements")
    op.drop_table("notes")
    for code in NEW_CODES:
        op.execute(sa.text("DELETE FROM permissions WHERE code = :code").bindparams(code=code))
