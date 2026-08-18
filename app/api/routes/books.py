from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_db
from app.schemas import BookCreate, BookRead, BookStatusUpdate

router = APIRouter(prefix="/books", tags=["books"])
DatabaseSession = Annotated[Session, Depends(get_db)]
SerialNumberPath = Annotated[
    str,
    Path(pattern=r"^[0-9]{6}$", description="Six-digit book serial number"),
]


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(data: BookCreate, session: DatabaseSession) -> BookRead:
    try:
        return services.create_book(session, data)
    except services.BookConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get("", response_model=list[BookRead])
def list_books(session: DatabaseSession) -> list[BookRead]:
    return services.list_books(session)


@router.patch("/{serial_number}/status", response_model=BookRead)
def update_book_status(
    serial_number: SerialNumberPath,
    data: BookStatusUpdate,
    session: DatabaseSession,
) -> BookRead:
    try:
        return services.update_book_status(session, serial_number, data)
    except services.BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except services.BookConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.delete("/{serial_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    serial_number: SerialNumberPath,
    session: DatabaseSession,
) -> Response:
    try:
        services.delete_book(session, serial_number)
    except services.BookNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except services.BookConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
