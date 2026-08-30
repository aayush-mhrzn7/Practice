"""bookmark notes, unique url, cascade fks, server defaults

Revision ID: 9c4e2a81b0d7
Revises: 080ff7a9278f
Create Date: 2026-08-30 17:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c4e2a81b0d7"
down_revision: Union[str, Sequence[str], None] = "080ff7a9278f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("bookmarks") as batch_op:
        batch_op.add_column(sa.Column("notes", sa.String(), nullable=True))
        batch_op.create_unique_constraint("uq_bookmarks_user_id_url", ["user_id", "url"])
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            existing_nullable=False,
        )

    with op.batch_alter_table("tags") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            existing_nullable=False,
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "created_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            existing_nullable=False,
        )

    op.create_table(
        "_bookmark_tags_new",
        sa.Column("bookmark_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bookmark_id"], ["bookmarks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("bookmark_id", "tag_id"),
    )
    op.execute(
        "INSERT INTO _bookmark_tags_new (bookmark_id, tag_id) SELECT bookmark_id, tag_id FROM bookmark_tags"
    )
    op.drop_table("bookmark_tags")
    op.rename_table("_bookmark_tags_new", "bookmark_tags")


def downgrade() -> None:
    op.create_table(
        "_bookmark_tags_old",
        sa.Column("bookmark_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bookmark_id"], ["bookmarks.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"]),
        sa.PrimaryKeyConstraint("bookmark_id", "tag_id"),
    )
    op.execute(
        "INSERT INTO _bookmark_tags_old (bookmark_id, tag_id) SELECT bookmark_id, tag_id FROM bookmark_tags"
    )
    op.drop_table("bookmark_tags")
    op.rename_table("_bookmark_tags_old", "bookmark_tags")

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("created_at", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)
        batch_op.alter_column("updated_at", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)

    with op.batch_alter_table("tags") as batch_op:
        batch_op.alter_column("created_at", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)
        batch_op.alter_column("updated_at", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)

    with op.batch_alter_table("bookmarks") as batch_op:
        batch_op.drop_constraint("uq_bookmarks_user_id_url", type_="unique")
        batch_op.drop_column("notes")
        batch_op.alter_column("created_at", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)
        batch_op.alter_column("updated_at", existing_type=sa.DateTime(), server_default=None, existing_nullable=False)
