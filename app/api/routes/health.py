from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import HealthRead

router = APIRouter(tags=["health"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/health", response_model=HealthRead)
def health(session: DatabaseSession) -> HealthRead:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from error
    return HealthRead(status="ok")
