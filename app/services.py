from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Book
from app.schemas import BookCreate, BookStatusUpdate


class BookNotFoundError(Exception):
    pass


class BookConflictError(Exception):
    pass


def create_book(session: Session, data: BookCreate) -> Book:
    book = Book(**data.model_dump(), is_borrowed=False)
    session.add(book)
    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise BookConflictError(
            "book with this serial number already exists"
        ) from error
    session.refresh(book)
    return book


def list_books(session: Session) -> list[Book]:
    statement = select(Book).order_by(Book.serial_number)
    return list(session.scalars(statement).all())


def update_book_status(
    session: Session,
    serial_number: str,
    data: BookStatusUpdate,
) -> Book:
    book = _get_book_for_update(session, serial_number)

    if book.is_borrowed == data.is_borrowed:
        state = "borrowed" if data.is_borrowed else "available"
        session.rollback()
        raise BookConflictError(f"book is already {state}")

    if data.is_borrowed:
        book.is_borrowed = True
        book.borrower_card_number = data.borrower_card_number
        book.borrowed_at = datetime.now(UTC)
    else:
        book.is_borrowed = False
        book.borrower_card_number = None
        book.borrowed_at = None

    session.commit()
    session.refresh(book)
    return book


def delete_book(session: Session, serial_number: str) -> None:
    book = _get_book_for_update(session, serial_number)
    if book.is_borrowed:
        session.rollback()
        raise BookConflictError("borrowed book cannot be deleted")

    session.delete(book)
    session.commit()


def _get_book_for_update(session: Session, serial_number: str) -> Book:
    statement = (
        select(Book).where(Book.serial_number == serial_number).with_for_update()
    )
    book = session.scalar(statement)
    if book is None:
        session.rollback()
        raise BookNotFoundError("book not found")
    return book
