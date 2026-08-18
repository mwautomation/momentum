from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (
        CheckConstraint(
            "serial_number ~ '^[0-9]{6}$'",
            name="ck_books_serial_number_six_digits",
        ),
        CheckConstraint("btrim(title) <> ''", name="ck_books_title_not_blank"),
        CheckConstraint("btrim(author) <> ''", name="ck_books_author_not_blank"),
        CheckConstraint(
            "borrower_card_number IS NULL OR borrower_card_number ~ '^[0-9]{6}$'",
            name="ck_books_borrower_card_six_digits",
        ),
        CheckConstraint(
            "(is_borrowed = true AND borrower_card_number IS NOT NULL "
            "AND borrowed_at IS NOT NULL) OR "
            "(is_borrowed = false AND borrower_card_number IS NULL "
            "AND borrowed_at IS NULL)",
            name="ck_books_borrowing_state_consistent",
        ),
    )

    serial_number: Mapped[str] = mapped_column(String(6), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    is_borrowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    borrower_card_number: Mapped[str | None] = mapped_column(
        String(6),
        nullable=True,
    )
    borrowed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
