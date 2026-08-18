import pytest
from pydantic import ValidationError

from app.schemas import BookCreate, BookStatusUpdate


def test_book_create_preserves_leading_zeroes_and_trims_text() -> None:
    book = BookCreate(
        serial_number="000123",
        title="  The Hobbit  ",
        author="  J. R. R. Tolkien  ",
    )

    assert book.serial_number == "000123"
    assert book.title == "The Hobbit"
    assert book.author == "J. R. R. Tolkien"


@pytest.mark.parametrize(
    "serial_number",
    ["12345", "1234567", "12345a", "１２３４５６", 123456],
)
def test_book_create_rejects_invalid_serial_numbers(serial_number: object) -> None:
    with pytest.raises(ValidationError):
        BookCreate(
            serial_number=serial_number,  # type: ignore[arg-type]
            title="The Hobbit",
            author="J. R. R. Tolkien",
        )


@pytest.mark.parametrize("field", ["title", "author"])
def test_book_create_rejects_blank_text(field: str) -> None:
    data = {
        "serial_number": "000123",
        "title": "The Hobbit",
        "author": "J. R. R. Tolkien",
    }
    data[field] = "   "

    with pytest.raises(ValidationError):
        BookCreate.model_validate(data)


def test_borrowing_requires_a_valid_card_number() -> None:
    with pytest.raises(ValidationError):
        BookStatusUpdate(is_borrowed=True)

    with pytest.raises(ValidationError):
        BookStatusUpdate(is_borrowed=True, borrower_card_number="12345a")

    status = BookStatusUpdate(
        is_borrowed=True,
        borrower_card_number="000001",
    )
    assert status.borrower_card_number == "000001"


@pytest.mark.parametrize("card_number", ["123456", None])
def test_returning_rejects_a_card_number_field(card_number: str | None) -> None:
    with pytest.raises(ValidationError):
        BookStatusUpdate(
            is_borrowed=False,
            borrower_card_number=card_number,
        )


def test_returning_accepts_only_the_state() -> None:
    status = BookStatusUpdate(is_borrowed=False)

    assert status.is_borrowed is False
    assert status.borrower_card_number is None
