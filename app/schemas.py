from datetime import datetime
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    StrictBool,
    StringConstraints,
    model_validator,
)

type SixDigitNumber = Annotated[
    str,
    StringConstraints(pattern=r"^[0-9]{6}$"),
]
type RequiredText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BookCreate(StrictSchema):
    serial_number: SixDigitNumber
    title: RequiredText
    author: RequiredText


class BookStatusUpdate(StrictSchema):
    is_borrowed: StrictBool
    borrower_card_number: SixDigitNumber | None = None

    @model_validator(mode="after")
    def validate_borrower(self) -> Self:
        if self.is_borrowed and self.borrower_card_number is None:
            raise ValueError("borrower_card_number is required when borrowing a book")
        if not self.is_borrowed and "borrower_card_number" in self.model_fields_set:
            raise ValueError(
                "borrower_card_number must be omitted when returning a book"
            )
        return self


class BookRead(BaseModel):
    serial_number: SixDigitNumber
    title: str
    author: str
    is_borrowed: bool
    borrower_card_number: SixDigitNumber | None
    borrowed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class HealthRead(BaseModel):
    status: str
