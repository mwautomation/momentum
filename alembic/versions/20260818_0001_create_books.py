"""Create the books table.

Revision ID: 20260818_0001
Revises:
Create Date: 2026-08-18
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260818_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("serial_number", sa.String(length=6), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("author", sa.Text(), nullable=False),
        sa.Column(
            "is_borrowed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("borrower_card_number", sa.String(length=6), nullable=True),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "btrim(author) <> ''",
            name="ck_books_author_not_blank",
        ),
        sa.CheckConstraint(
            "borrower_card_number IS NULL OR borrower_card_number ~ '^[0-9]{6}$'",
            name="ck_books_borrower_card_six_digits",
        ),
        sa.CheckConstraint(
            "(is_borrowed = true AND borrower_card_number IS NOT NULL "
            "AND borrowed_at IS NOT NULL) OR "
            "(is_borrowed = false AND borrower_card_number IS NULL "
            "AND borrowed_at IS NULL)",
            name="ck_books_borrowing_state_consistent",
        ),
        sa.CheckConstraint(
            "serial_number ~ '^[0-9]{6}$'",
            name="ck_books_serial_number_six_digits",
        ),
        sa.CheckConstraint(
            "btrim(title) <> ''",
            name="ck_books_title_not_blank",
        ),
        sa.PrimaryKeyConstraint("serial_number"),
    )


def downgrade() -> None:
    op.drop_table("books")
